import json
import logging
from typing import List, Dict, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_insights_and_questions(scored_themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate evidence-backed insight hypotheses and non-leading research questions.
    Respects 3-Tier Research Relevance (DIRECT, INDIRECT, OUT_OF_SCOPE).
    If OUT_OF_SCOPE -> STOP and set out of scope without inventing an insight.
    """
    api_key = config.LLM_API_KEY
    use_llm = bool(api_key)
    client = None

    if use_llm:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=config.LLM_BASE_URL)
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
            use_llm = False

    enriched_results = []
    for item in scored_themes:
        theme = item["theme"]
        quotes = item["example_quotes"]
        action = item["action"]
        relevance = item.get("research_relevance", "OUT_OF_SCOPE")
        mech = item.get("behavioral_mechanism", "")
        primary_issue = item.get("primary_issue", "Other")

        # If Out of Scope -> STOP! Do not force an insight or question!
        if relevance == "OUT_OF_SCOPE" or action == "Out of Scope for Research Objective":
            item["suggested_insight"] = ""
            item["suggested_research_question"] = ""
            item["status"] = "Out of Scope"
            if not item.get("out_of_scope_reason"):
                item["out_of_scope_reason"] = f"This theme represents operational feedback in {primary_issue} without a direct causal link to category exploration."
            enriched_results.append(item)
            continue

        item["status"] = "In Scope"
        suggested_insight = ""
        suggested_question = ""

        if use_llm and client:
            try:
                prompt = f"""You are a Principal User Researcher.
Synthesize an evidence-backed insight hypothesis and non-leading research question for this cluster.

Theme: {theme}
Primary Issue: {primary_issue}
Relevance: {relevance}
Mechanism from Quotes: {mech}
Customer Quotes:
""" + "\n".join([f"- {q}" for q in quotes]) + """

RULES:
1. EVIDENCE CHECK: Every claim must be supported by the quotes above.
2. The Research Hypothesis MUST explicitly state the business metric "purchase from a new category".
3. Suggested Research Question must be an open-ended, non-leading 30-minute interview question probing past actions.

Respond ONLY with JSON:
{
  "suggested_insight": "<hypothesis explicitly mentioning category trial metric>",
  "suggested_research_question": "<open-ended non-leading interview question>"
}"""

                resp = client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                parsed = json.loads(resp.choices[0].message.content)
                suggested_insight = parsed.get("suggested_insight", "")
                suggested_question = parsed.get("suggested_research_question", "")
            except Exception as e:
                logger.warning(f"LLM question generation error for '{theme}': {e}")

        # Fallback if LLM omitted or failed
        if not suggested_insight:
            if "Refund" in theme or "Return" in theme or "Risk" in theme:
                suggested_insight = "If customers trust that post-purchase refund issues will be resolved fairly, they will be more willing to purchase from unfamiliar or higher-risk product categories."
                suggested_question = "Tell me about the last time you considered buying a product outside your usual categories on Blinkit—what specific return assurances did you look for before deciding?"
            else:
                suggested_insight = f"If customer confidence in product quality and fulfillment reliability is increased, then customers will be more willing to purchase from new product categories."
                suggested_question = f"Walk me through your decision process when considering purchases outside your regular order list."

        item["suggested_insight"] = suggested_insight
        item["suggested_research_question"] = suggested_question
        enriched_results.append(item)

    logger.info("Completed evidence-backed insight and question generation.")
    return enriched_results

if __name__ == "__main__":
    pass
