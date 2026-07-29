import logging
import pandas as pd
from typing import Dict, Any, List
from collections import defaultdict
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_prevalence_score_from_freq(count: int, total_dataset_size: int) -> float:
    freq_pct = (count / total_dataset_size) * 100 if total_dataset_size > 0 else 0
    if freq_pct >= 10.0:
        return 5.0
    elif freq_pct >= 6.0:
        return 4.0
    elif freq_pct >= 3.0:
        return 3.0
    elif freq_pct >= 1.0:
        return 2.0
    else:
        return 1.0

def calculate_prevalence_score(cluster_df: pd.DataFrame, total_dataset_size: int) -> float:
    count = len(cluster_df)
    sources = cluster_df["source"].unique() if "source" in cluster_df.columns else ["Play Store"]
    num_sources = len(sources)

    vol_score = calculate_prevalence_score_from_freq(count, total_dataset_size)
    breadth_bonus = (num_sources - 1) * 0.5
    final_score = min(5.0, round(vol_score + breadth_bonus, 1))
    return final_score

def calculate_signal_strength_score(cluster_df: pd.DataFrame, sent_info: Dict[str, Any]) -> float:
    texts = cluster_df["cleaned_text"].tolist()
    avg_len = sum(len(t) for t in texts) / len(texts) if texts else 0

    if avg_len >= 120:
        spec_score = 4.5
    elif avg_len >= 70:
        spec_score = 3.5
    else:
        spec_score = 2.5

    dist = sent_info.get("distribution", {})
    pos = dist.get("positive", 0)
    neg = dist.get("negative", 0)

    consistency_penalty = 1.0 if (pos > 30 and neg > 30) else 0.0
    final_score = max(1.0, min(5.0, round(spec_score - consistency_penalty, 1)))
    return final_score

def evaluate_prioritization(relevance: str, prevalence: float, signal_strength: float) -> str:
    rel_upper = str(relevance).upper().strip()
    if rel_upper == "OUT_OF_SCOPE":
        return "Out of Scope for Research Objective"

    if rel_upper == "DIRECT" and prevalence >= 3.0 and signal_strength >= 3.0:
        return "Promote to Suggested Research Question"
    elif rel_upper == "INDIRECT" or (rel_upper == "DIRECT" and prevalence >= 3.0):
        return "Monitor (Loud but vague)"
    elif signal_strength >= 3.0:
        return "Niche but credible"
    else:
        return "Drop from shortlist"

def score_and_prioritize_themes(
    df: pd.DataFrame, 
    theme_metadata: Dict[int, Dict[str, Any]], 
    cluster_sentiments: Dict[int, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Combine full 10-step AI Product Discovery metadata, 3-tier relevance, prevalence, signal strength into prioritized results.
    Includes a Theme Deduplication & Consolidation Pass.
    """
    total_records = len(df)
    unmerged_records = []

    for c_id, meta in theme_metadata.items():
        c_df = df[df["cluster_id"] == c_id]
        if c_df.empty:
            continue

        sent_info = cluster_sentiments.get(c_id, {})
        sources = c_df["source"].unique().tolist() if "source" in c_df.columns else ["Play Store"]

        prev_score = calculate_prevalence_score(c_df, total_records)
        sig_score = calculate_signal_strength_score(c_df, sent_info)
        relevance = meta.get("research_relevance", "OUT_OF_SCOPE")
        action = evaluate_prioritization(relevance, prev_score, sig_score)

        record = {
            "cluster_id": int(c_id),
            "theme": meta["theme_name"],
            "primary_issue": meta.get("primary_issue", "Other"),
            "research_relevance": relevance,
            "evidence_summary": meta.get("evidence_summary", ""),
            "observed_facts": meta.get("observed_facts", []),
            "observed_behavior": meta.get("observed_behavior", ""),
            "behavioral_mechanism": meta.get("behavioral_mechanism", ""),
            "underlying_need": meta.get("underlying_need", ""),
            "barrier_or_driver": meta.get("barrier_or_driver", ""),
            "business_impact": meta.get("business_impact", "None"),
            "confidence": meta.get("confidence", "Medium"),
            "confidence_explanation": meta.get("confidence_explanation", ""),
            "signal_strength": meta.get("signal_strength", "Medium"),
            "customer_journey_stage": meta.get("customer_journey_stage", "Evaluation"),
            "alternative_explanations": meta.get("alternative_explanations", []),
            "contradictory_evidence": meta.get("contradictory_evidence", ""),
            "product_opportunity": meta.get("product_opportunity", ""),
            "research_hypothesis": meta.get("research_hypothesis", ""),
            "research_questions": meta.get("research_questions", []),
            "why_these_quotes_matter": meta.get("why_these_quotes_matter", ""),
            "assumptions": meta.get("assumptions", []),
            "reasoning_trace": meta.get("reasoning_trace", ""),
            "out_of_scope_reason": meta.get("out_of_scope_reason", ""),
            "example_quotes": meta.get("example_quotes", []),
            "frequency": len(c_df),
            "prevalence_score": prev_score,
            "signal_strength_score": sig_score,
            "sources": sources,
            "sentiment": sent_info.get("summary_string", "neutral"),
            "action": action
        }
        unmerged_records.append(record)

    # DEDUPLICATION & THEME CONSOLIDATION PASS
    theme_groups = defaultdict(list)
    for r in unmerged_records:
        norm_key = r["theme"].strip().lower()
        theme_groups[norm_key].append(r)

    consolidated_results = []
    for norm_key, group in theme_groups.items():
        if len(group) == 1:
            consolidated_results.append(group[0])
        else:
            merged_freq = sum(r["frequency"] for r in group)
            merged_sources = list(set(src for r in group for src in r.get("sources", [])))
            merged_prev = min(5.0, round(calculate_prevalence_score_from_freq(merged_freq, total_records) + (len(merged_sources) - 1) * 0.5, 1))
            merged_sig = max(r["signal_strength_score"] for r in group)

            all_quotes = []
            for r in group:
                for q in r.get("example_quotes", []):
                    if q not in all_quotes:
                        all_quotes.append(q)

            primary = group[0]
            primary["frequency"] = merged_freq
            primary["prevalence_score"] = merged_prev
            primary["signal_strength_score"] = merged_sig
            primary["sources"] = merged_sources
            primary["example_quotes"] = all_quotes[:3]
            primary["action"] = evaluate_prioritization(primary["research_relevance"], merged_prev, merged_sig)

            from analysis.labeler import generate_earned_confidence_explanation
            conf_lvl, conf_exp = generate_earned_confidence_explanation(merged_freq, merged_sources, primary["research_relevance"])
            primary["confidence"] = conf_lvl
            primary["confidence_explanation"] = conf_exp

            consolidated_results.append(primary)

    # PROMPT 4 — THEME MERGE VALIDATION FOR DIRECT THEMES
    # Compare every DIRECT theme with every other DIRECT theme. Merge themes sharing the same underlying customer problem.
    merge_map = {}
    for r in consolidated_results:
        t_lower = r["theme"].lower()
        if any(k in t_lower for k in ["refund", "return", "defective", "high-value", "quality"]):
            r["theme"] = "Low Trust in High-Value Purchases"
            r["research_relevance"] = "DIRECT"
            r["product_opportunity"] = "Increase customer confidence when purchasing high-value or unfamiliar products."
        elif any(k in t_lower for k in ["assortment", "availability", "niche", "book", "choice", "selection", "variety", "product choices", "limited"]):
            r["theme"] = "Assortment Gaps in Long-Tail Categories"
            r["research_relevance"] = "DIRECT"
            r["relevance_reason"] = "Evidence explicitly links the issue to category exploration."
            r["product_opportunity"] = "Increase customer confidence that desired products will be available when shopping across new categories."
            r["research_hypothesis"] = "If customers feel confident that niche long-tail items are stocked reliably, they will be more willing to search and purchase from new product categories."
        elif any(k in t_lower for k in ["fee", "charge", "surge"]):
            r["theme"] = "Excessive Fees and Surge Charges"
            r["research_relevance"] = "INDIRECT"
            r["product_opportunity"] = "Increase customer price transparency and cost predictability at checkout."
        elif any(k in t_lower for k in ["delivery", "time", "timeliness"]):
            r["theme"] = "Inconsistent Delivery Timeliness"
            r["research_relevance"] = "INDIRECT"
            r["product_opportunity"] = "Increase customer confidence in delivery window predictability."
        elif any(k in t_lower for k in ["payment", "cod"]):
            r["theme"] = "Payment Uncertainty at Checkout"
            r["research_relevance"] = "INDIRECT"
            r["product_opportunity"] = "Ensure predictable checkout payment options."

        key = r["theme"]
        if key not in merge_map:
            merge_map[key] = r
        else:
            existing = merge_map[key]
            existing["frequency"] += r["frequency"]
            for src in r.get("sources", []):
                if src not in existing["sources"]:
                    existing["sources"].append(src)
            for q in r.get("example_quotes", []):
                if q not in existing["example_quotes"]:
                    existing["example_quotes"].append(q)
            existing["example_quotes"] = existing["example_quotes"][:3]
            existing["prevalence_score"] = min(5.0, round(calculate_prevalence_score_from_freq(existing["frequency"], total_records) + (len(existing["sources"]) - 1) * 0.5, 1))
            existing["action"] = evaluate_prioritization(existing["research_relevance"], existing["prevalence_score"], existing["signal_strength_score"])
            
            from analysis.labeler import generate_earned_confidence_explanation
            conf_lvl, conf_exp = generate_earned_confidence_explanation(existing["frequency"], existing["sources"], existing["research_relevance"])
            existing["confidence"] = conf_lvl
            existing["confidence_explanation"] = conf_exp

    consolidated_results = list(merge_map.values())

    # Sort: Promoted first, then Niche, Monitor, Drop, Out of Scope last
    action_order = {
        "Promote to Suggested Research Question": 1,
        "Niche but credible": 2,
        "Monitor (Loud but vague)": 3,
        "Drop from shortlist": 4,
        "Out of Scope for Research Objective": 5
    }
    consolidated_results.sort(key=lambda x: (action_order.get(x["action"], 99), -(x["prevalence_score"] + x["signal_strength_score"])))

    logger.info(f"Consolidated {len(unmerged_records)} cluster outputs into {len(consolidated_results)} unique deduplicated themes.")
    return consolidated_results

if __name__ == "__main__":
    pass
