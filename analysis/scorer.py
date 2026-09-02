import logging
import pandas as pd
from typing import Dict, Any, List
from collections import defaultdict
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_prevalence_score_from_freq(count: int, total_dataset_size: int) -> float:
    freq_pct = (count / total_dataset_size) * 100 if total_dataset_size > 0 else 0
    if freq_pct >= 25.0:
        return 5.0
    elif freq_pct >= 15.0:
        return 4.5
    elif freq_pct >= 5.0:
        return 4.0
    elif freq_pct >= 2.0:
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

    if avg_len >= 100:
        spec_score = 4.5
    elif avg_len >= 50:
        spec_score = 4.0
    else:
        spec_score = 3.0

    return spec_score

def evaluate_prioritization(relevance: str, prevalence: float, signal_strength: float) -> str:
    rel_upper = str(relevance).upper().strip()
    if rel_upper == "OUT_OF_SCOPE":
        return "Out of Scope for Research Objective"

    if rel_upper == "DIRECT" and prevalence >= 3.5 and signal_strength >= 3.5:
        return "Promote to Suggested Research Question"
    elif rel_upper == "INDIRECT" or (rel_upper == "DIRECT" and prevalence >= 3.0):
        return "Monitor (Loud but vague)"
    elif signal_strength >= 3.5:
        return "Niche but credible"
    else:
        return "Drop from shortlist"

def score_and_prioritize_themes(
    df: pd.DataFrame, 
    theme_metadata: Dict[int, Dict[str, Any]], 
    cluster_sentiments: Dict[int, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Score and prioritize verified 6-pillar themes.
    """
    total_records = len(df)
    theme_records = []

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

        count = len(c_df)
        pct = round((count / total_records) * 100, 1)

        record = {
            "cluster_id": int(c_id),
            "theme": meta["theme_name"],
            "primary_issue": meta.get("primary_issue", "Other"),
            "research_relevance": relevance,
            "evaluator_cluster": meta.get("evaluator_cluster", "High-Intent Evaluator"),
            "evidence_summary": meta.get("evidence_summary", ""),
            "observed_facts": meta.get("observed_facts", []),
            "observed_behavior": meta.get("observed_behavior", ""),
            "behavioral_mechanism": meta.get("behavioral_mechanism", ""),
            "underlying_need": meta.get("underlying_need", ""),
            "barrier_or_driver": meta.get("barrier_or_driver", ""),
            "business_impact": meta.get("business_impact", "High"),
            "confidence": meta.get("confidence", "High"),
            "confidence_explanation": meta.get("confidence_explanation", ""),
            "signal_strength": meta.get("signal_strength", "High"),
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
            "frequency": count,
            "percentage_share": pct,
            "prevalence_score": prev_score,
            "signal_strength_score": sig_score,
            "sources": sources,
            "sentiment": sent_info.get("summary_string", "mixed"),
            "action": action
        }
        theme_records.append(record)

    # Sort: Promoted first, then Niche, Monitor, Drop, Out of Scope last
    action_order = {
        "Promote to Suggested Research Question": 1,
        "Niche but credible": 2,
        "Monitor (Loud but vague)": 3,
        "Drop from shortlist": 4,
        "Out of Scope for Research Objective": 5
    }
    theme_records.sort(key=lambda x: (action_order.get(x["action"], 99), -x["frequency"]))

    logger.info(f"Consolidated {len(theme_records)} clean, prioritized behavioral themes.")
    return theme_records

if __name__ == "__main__":
    pass
