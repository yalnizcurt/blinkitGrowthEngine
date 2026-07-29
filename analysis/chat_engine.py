import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Blinkit ReviewLens AI Chat Assistant.
Your purpose is to help Product Managers interact with customer feedback data, research hypotheses, and underlying behavioral mechanisms.

STRICT GROUNDED RAG RULES:
1. Answer ONLY using the customer feedback evidence, themes, and quotes provided in the Context block below.
2. Never invent quotes or claim facts not supported by the evidence context.
3. Always cite specific customer quotes when answering.
4. If the user asks a question that CANNOT be answered from the provided customer feedback, state politely: "No relevant data found in customer feedback corpus for this question."
5. Never recommend UI widgets, features, or badges. Maintain product discovery principles (capabilities, behavioral mechanisms, JTBD).

Format your output as a JSON object:
{
  "reply": "<Markdown formatted detailed response grounded in evidence>",
  "citations": [
    {
      "theme": "<Theme title>",
      "quote": "<Verbatim customer quote>",
      "source": "<Source name (Play Store / App Store / Reddit)>"
    }
  ],
  "suggested_followups": [
    "<Suggested follow-up question 1>",
    "<Suggested follow-up question 2>"
  ]
}"""

def build_rag_context() -> str:
    """
    Build structured RAG context from final results JSON.
    """
    json_path = config.FINAL_RESULTS_JSON
    if not json_path.exists():
        return "No customer review data available. Please run the pipeline first."

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data.get("metadata", {})
        themes = data.get("themes", [])

        context_lines = [
            f"=== BLINKIT CUSTOMER FEEDBACK CORPUS CONTEXT ===",
            f"Total Feedback Analyzed: {meta.get('total_feedback_analyzed', 0)} clean items",
            f"Total Unique Themes: {meta.get('total_themes_discovered', 0)}",
            f"Promoted Interview Hypotheses: {meta.get('promoted_research_questions_count', 0)}",
            f"Out of Scope Themes: {meta.get('out_of_scope_themes_count', 0)}\n",
            "--- DISCOVERED THEMES & BEHAVIORAL MECHANISMS ---"
        ]

        for t in themes:
            context_lines.append(f"\nTheme: \"{t.get('theme')}\"")
            context_lines.append(f"  Primary Area: {t.get('primary_issue')}")
            context_lines.append(f"  Relevance: {t.get('research_relevance')}")
            context_lines.append(f"  Journey Stage: {t.get('customer_journey_stage')}")
            context_lines.append(f"  Observed Facts: {', '.join(t.get('observed_facts', []))}")
            context_lines.append(f"  Observed Behavior: {t.get('observed_behavior')}")
            context_lines.append(f"  Behavioral Mechanism: {t.get('behavioral_mechanism')}")
            context_lines.append(f"  Underlying Need / JTBD: {t.get('underlying_need')}")
            context_lines.append(f"  Barrier / Driver: {t.get('barrier_or_driver')}")
            context_lines.append(f"  Business Impact: {t.get('business_impact')} | Confidence: {t.get('confidence')}")
            context_lines.append(f"  Product Opportunity: {t.get('product_opportunity')}")
            context_lines.append(f"  Research Question: {t.get('suggested_research_question')}")
            context_lines.append(f"  Action / Priority: {t.get('action')}")
            if t.get('out_of_scope_reason'):
                context_lines.append(f"  Out of Scope Reason: {t.get('out_of_scope_reason')}")
            context_lines.append("  Customer Quotes:")
            for q in t.get('example_quotes', []):
                context_lines.append(f"    - \"{q}\"")

        return "\n".join(context_lines)
    except Exception as e:
        logger.error(f"Error building RAG context: {e}")
        return "Error building RAG context from data files."

def generate_chat_response(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Generate grounded AI chat reply using Groq API and LLaMA 3.3 70B.
    """
    rag_context = build_rag_context()
    user_query = messages[-1].get("content", "") if messages else ""

    client = OpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL
    )

    full_messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{rag_context}"}
    ]

    # Include conversation history (last 5 messages)
    for m in messages[-5:]:
        full_messages.append({"role": m["role"], "content": m["content"]})

    try:
        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=full_messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = resp.choices[0].message.content
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        logger.error(f"Groq Chat API error: {e}")
        return {
            "reply": f"Sorry, I encountered an error querying the Groq AI model: {str(e)}",
            "citations": [],
            "suggested_followups": [
                "What are the top reasons users avoid non-grocery items?",
                "What operational issues were routed as out of scope?"
            ]
        }

if __name__ == "__main__":
    test_msgs = [{"role": "user", "content": "What are the main reasons users hesitate to buy non-grocery products?"}]
    res = generate_chat_response(test_msgs)
    print(json.dumps(res, indent=2))
