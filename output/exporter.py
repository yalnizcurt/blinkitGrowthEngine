import json
import logging
import pandas as pd
from typing import List, Dict, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def export_all_formats(results: List[Dict[str, Any]], total_feedback_count: int) -> Dict[str, str]:
    """
    Export final results to CSV, JSON, and Markdown summary files following AI Product Discovery Engine System Prompt.
    """
    # 1. Export CSV (Complete System Prompt Audit Trail Schema)
    csv_rows = []
    for r in results:
        csv_rows.append({
            "Theme": r.get("theme", ""),
            "Primary Issue": r.get("primary_issue", ""),
            "Research Relevance": r.get("research_relevance", ""),
            "Evidence Summary": r.get("evidence_summary", ""),
            "Observed Facts": "; ".join(r.get("observed_facts", [])),
            "Observed Behavior": r.get("observed_behavior", ""),
            "Behavioral Mechanism": r.get("behavioral_mechanism", ""),
            "Underlying Need / JTBD": r.get("underlying_need", ""),
            "Barrier / Driver": r.get("barrier_or_driver", ""),
            "Business Impact": r.get("business_impact", ""),
            "Confidence": r.get("confidence", ""),
            "Confidence Explanation": r.get("confidence_explanation", ""),
            "Signal Strength": r.get("signal_strength", ""),
            "Customer Journey Stage": r.get("customer_journey_stage", ""),
            "Alternative Explanations": "; ".join(r.get("alternative_explanations", [])),
            "Contradictory Evidence": r.get("contradictory_evidence", ""),
            "Product Opportunity": r.get("product_opportunity", ""),
            "Research Hypothesis": r.get("research_hypothesis", ""),
            "Research Questions": "; ".join(r.get("research_questions", [])),
            "Why These Quotes Matter": r.get("why_these_quotes_matter", ""),
            "Assumptions": "; ".join(r.get("assumptions", [])),
            "Reasoning Trace": r.get("reasoning_trace", ""),
            "Prevalence Score (1-5)": r.get("prevalence_score", 0),
            "Mention Count": r.get("frequency", 0),
            "Sources": ", ".join(r.get("sources", [])),
            "Example Quote 1": r.get("example_quotes", [""])[0] if len(r.get("example_quotes", [])) > 0 else "",
            "Example Quote 2": r.get("example_quotes", [""])[1] if len(r.get("example_quotes", [])) > 1 else "",
            "Example Quote 3": r.get("example_quotes", [""])[2] if len(r.get("example_quotes", [])) > 2 else "",
            "Action / Priority": r.get("action", ""),
            "Out of Scope Reason": r.get("out_of_scope_reason", "")
        })

    df_csv = pd.DataFrame(csv_rows)
    df_csv.to_csv(config.FINAL_RESULTS_CSV, index=False)
    logger.info(f"Saved primary results CSV to {config.FINAL_RESULTS_CSV}")

    # 2. Coverage Warning Analysis
    all_sources_flat = [src for r in results for src in r.get("sources", [])]
    playstore_pct = (all_sources_flat.count("play_store") / len(all_sources_flat) * 100) if all_sources_flat else 0
    coverage_warning = ""
    if playstore_pct > 70:
        coverage_warning = f"Coverage Warning: Dataset is dominated by Google Play Store ({playstore_pct:.1f}%); deep qualitative community sources (Reddit) are underrepresented."

    # 3. Export JSON
    json_data = {
        "metadata": {
            "total_feedback_analyzed": total_feedback_count,
            "total_themes_discovered": len(results),
            "promoted_research_questions_count": sum(1 for r in results if r.get("action") == "Promote to Suggested Research Question"),
            "out_of_scope_themes_count": sum(1 for r in results if r.get("action") == "Out of Scope for Research Objective"),
            "coverage_warning": coverage_warning
        },
        "themes": results
    }
    with open(config.FINAL_RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved results JSON to {config.FINAL_RESULTS_JSON}")

    # 4. Export Executive Markdown Summary
    md_content = generate_markdown_report(results, total_feedback_count, coverage_warning)
    with open(config.FINAL_SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    logger.info(f"Saved summary Markdown report to {config.FINAL_SUMMARY_MD}")

    return {
        "csv": str(config.FINAL_RESULTS_CSV),
        "json": str(config.FINAL_RESULTS_JSON),
        "markdown": str(config.FINAL_SUMMARY_MD)
    }

def generate_markdown_report(results: List[Dict[str, Any]], total_count: int, coverage_warning: str) -> str:
    promoted = [r for r in results if r.get("action") == "Promote to Suggested Research Question"]
    monitored = [r for r in results if "Monitor" in r.get("action", "")]
    niche = [r for r in results if "Niche" in r.get("action", "")]
    out_of_scope = [r for r in results if r.get("action") == "Out of Scope for Research Objective"]

    md = []
    md.append("# AI Product Discovery Engine — Master Knowledge Report\n")
    md.append("**Business Objective**: *Increase percentage of Monthly Active Customers purchasing from at least one new category every month.*\n\n")
    md.append(f"**Total Feedback Analyzed**: {total_count} clean customer items across Play Store, App Store, and Reddit.\n")
    if coverage_warning:
        md.append(f"⚠️ **{coverage_warning}**\n\n")

    md.append("## 🎯 Promoted Product Opportunities & Auditable Reasoning Chains\n")
    if not promoted:
        md.append("_No themes met the dual High Category Impact + High Signal Strength threshold._\n")
    for idx, p in enumerate(promoted, 1):
        md.append(f"### {idx}. {p['theme']}\n")
        md.append(f"- **Primary Issue**: `{p.get('primary_issue', 'General')}` | **Relevance**: `{p.get('research_relevance', 'YES')}` | **Journey Stage**: `{p.get('customer_journey_stage', 'Evaluation')}`\n")
        md.append(f"- **Business Impact**: `{p.get('business_impact', 'High')}` | **Confidence**: `{p.get('confidence', 'High')}` ({p.get('confidence_explanation')})\n")
        md.append(f"- **Evidence Summary**: {p.get('evidence_summary', 'N/A')}\n")
        md.append(f"- **Observed Facts**: {', '.join(p.get('observed_facts', []))}\n")
        md.append(f"- **Observed Behavior (WHAT)**: {p.get('observed_behavior', 'N/A')}\n")
        md.append(f"- **Behavioral Mechanism (WHY)**: *\"{p.get('behavioral_mechanism', 'N/A')}\"*\n")
        md.append(f"- **Underlying Need / JTBD**: {p.get('underlying_need', 'N/A')}\n")
        md.append(f"- **Barrier / Driver**: {p.get('barrier_or_driver', 'N/A')}\n")
        md.append(f"- **Product Opportunity (Solution-Agnostic)**: 🚀 **\"{p.get('product_opportunity', '')}\"**\n")
        md.append(f"- **Research Hypothesis**: 🧪 *\"{p.get('research_hypothesis', '')}\"*\n")
        md.append(f"- **Research Questions**: {', '.join([f'\"{q}\"' for q in p.get('research_questions', [])])}\n")
        md.append(f"- **Alternative Explanations**: {', '.join(p.get('alternative_explanations', []))}\n")
        md.append(f"- **Contradictory Evidence**: {p.get('contradictory_evidence', 'None')}\n")
        md.append(f"- **Assumptions**: {', '.join(p.get('assumptions', []))}\n")
        md.append(f"- **Full Reasoning Trace**: `{p.get('reasoning_trace')}`\n")
        md.append("- **Supporting Verbatim Customer Evidence**:\n")
        for q in p.get("example_quotes", [])[:3]:
            md.append(f"  > \"{q}\"\n")
        md.append("\n---\n")

    if monitored or niche:
        md.append("\n## 📊 Secondary / Monitored Signals\n")
        for m in monitored + niche:
            md.append(f"- **{m['theme']}** (`{m.get('primary_issue')}`) — Stage: {m.get('customer_journey_stage')} | Impact: {m.get('business_impact')} | Confidence: {m.get('confidence')}\n")

    md.append("\n## 🛑 Out of Scope Themes (Routed to Operational Product Teams)\n")
    if not out_of_scope:
        md.append("_None_\n")
    for o in out_of_scope:
        md.append(f"### 📌 {o['theme']}\n")
        md.append(f"- **Primary Area**: `{o.get('primary_issue', 'General')}` | **Journey Stage**: `{o.get('customer_journey_stage', 'N/A')}` | **Mentions**: {o['frequency']}\n")
        md.append(f"- **Out of Scope Rationale**: {o.get('out_of_scope_reason', 'Operational product feedback with no category trial link.')}\n")
        md.append("- **Sample Quote**:\n")
        if o.get("example_quotes"):
            md.append(f"  > \"{o['example_quotes'][0]}\"\n")
        md.append("\n")

    return "\n".join(md)

if __name__ == "__main__":
    pass
