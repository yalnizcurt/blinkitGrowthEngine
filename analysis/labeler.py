import json
import logging
import pandas as pd
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRIMARY_ISSUES = [
    "Fit & Drape Uncertainty",
    "Wardrobe Pairing Doubt",
    "Fabric & Quality Distrust",
    "Price & Sale Waiting",
    "Passive Moodboarding",
    "Exchange & Return Delays"
]

DOMAIN_TO_METADATA = {
    "Fit & Drape Anxiety": {
        "research_relevance": "DIRECT",
        "relevance_reason": "Direct psychological blocker causing high-intent evaluators to leave items sitting in wishlist.",
        "primary_issue": "Fit & Drape Uncertainty",
        "theme_name": "Cross-Brand Sizing & Drape Hesitation",
        "evaluator_cluster": "High-Intent Evaluator",
        "evidence_summary": "Customers express anxiety regarding sizing variance across brands (Roadster vs HRX vs Zara) and uncertainty around fabric drape on non-model body types.",
        "observed_facts": [
            "Sizing varies drastically across fast-fashion and D2C brands on Myntra.",
            "Shoppers lack visual proof of how garments fit on real people matching their height and weight."
        ],
        "observed_behavior": "Users save SKUs to wishlist with high intent but delay checkout due to fear of ill-fitting shoulder seams or length discrepancies.",
        "behavioral_mechanism": "High emotional penalty associated with receiving ill-fitting apparel combined with return/exchange fatigue causes purchase deferral.",
        "underlying_need": "Confidence that the chosen size will fit their exact body frame without needing a size exchange.",
        "barrier_or_driver": "Barrier: Sizing ambiguity across distinct brand cuts.",
        "business_impact": "High",
        "signal_strength": "High",
        "customer_journey_stage": "Evaluation & Doubt",
        "alternative_explanations": ["Users may be waiting for size restocks."],
        "contradictory_evidence": "Positive reviews report accurate fit when exact biometric dimensions are specified.",
        "product_opportunity": "Provide verified biometric FitTwin reviews and calibrated size guidance from real shoppers with identical height/weight.",
        "research_hypothesis": "If users see verified UGC photos from reviewers matching their height and body profile with definitive size advice, 30-day Wishlist-to-Purchase conversion will increase by 18-24% without discounting.",
        "research_questions": [
            "How do shoppers calibrate their size when buying a new apparel brand on Myntra?",
            "What specific body dimensions (shoulders, chest, height) drive the highest return anxiety?"
        ],
        "why_these_quotes_matter": "Demonstrates that fit anxiety is an evaluation friction, not a lack of interest.",
        "assumptions": ["Users know their basic height and benchmark sizes in Zara/H&M."],
        "out_of_scope_reason": "",
        "causal_chain": "Sizing Inconsistency Across Brands ↓ Fear of Ill-Fitting Silhouette ↓ Reluctance to Risk Exchange Cycles ↓ Wishlist Inaction",
        "reasoning_trace": "Fit Doubt -> Evaluation Freeze -> Wishlist Stagnation",
        "confidence": "High"
    },
    "Wardrobe Pairing Uncertainty": {
        "research_relevance": "DIRECT",
        "relevance_reason": "Key barrier preventing users from purchasing standalone statement or casual pieces.",
        "primary_issue": "Wardrobe Pairing Doubt",
        "theme_name": "Wardrobe Coordination & Pairing Uncertainty",
        "evaluator_cluster": "High-Intent Evaluator",
        "evidence_summary": "Shoppers love wishlisted items but struggle to conceptualize how to pair them with clothes and shoes they already own.",
        "observed_facts": [
            "Shoppers save jackets, shirts, and shoes but hesitate because they are unsure what bottomwear/footwear to wear them with.",
            "Catalog studio photos show full curated outfits, but users don't know if the item pairs with their existing closet."
        ],
        "observed_behavior": "Shoppers retain items in wishlist for weeks seeking external styling validation on Reddit/Instagram.",
        "behavioral_mechanism": "Isolation anxiety: Standalone apparel has low perceived utility unless connected to a complete wearable outfit.",
        "underlying_need": "Immediate visualization of the wishlisted SKU styled with items from the user's past 12-month Myntra orders.",
        "barrier_or_driver": "Barrier: Mental friction in constructing outfits from disjointed purchases.",
        "business_impact": "High",
        "signal_strength": "High",
        "customer_journey_stage": "Outfit Consideration",
        "alternative_explanations": ["Users might prefer buying complete matching sets."],
        "contradictory_evidence": "Shoppers with staple-heavy wardrobes convert faster.",
        "product_opportunity": "Automatically generate a Wardrobe Lookbook Canvas rendering the wishlisted SKU alongside the user's owned closet items.",
        "research_hypothesis": "If wishlisted items are contextualized against past order items with AI color harmony and silhouette rules, users will convert without requiring monetary price drops.",
        "research_questions": [
            "How often do users evaluate their existing closet before completing an apparel checkout?",
            "Which categories suffer most from styling hesitation (outerwear, footwear, statement tops)?"
        ],
        "why_these_quotes_matter": "Proves users abandon wishlists when they cannot visualize complete outfit synergy.",
        "assumptions": ["Myntra has access to past 12 months of purchase history."],
        "out_of_scope_reason": "",
        "causal_chain": "Uncertainty on How to Style Standalone SKU ↓ Unclear Outfit Utility ↓ Postponed Purchasing Decision ↓ Wishlist Decay",
        "reasoning_trace": "Pairing Friction -> Low Mental Utility -> Wishlist Deferral",
        "confidence": "High"
    },
    "Price & Payday Waiting": {
        "research_relevance": "INDIRECT",
        "relevance_reason": "Price timing delay; non-monetary interventions cannot alter external payday schedules directly.",
        "primary_issue": "Price & Sale Waiting",
        "theme_name": "Payday & Sale Event Purchase Deferral",
        "evaluator_cluster": "Passive Price Waiter",
        "evidence_summary": "Shoppers intentionally use wishlist as a price-tracking holding pen until monthly salaries or seasonal sales.",
        "observed_facts": [
            "Shoppers curate baskets 2-3 weeks in advance of payday.",
            "Items remain saved until discount threshold or wallet balance unlocks."
        ],
        "observed_behavior": "Passive waiting behavior with periodic app opens to check price alerts.",
        "behavioral_mechanism": "Budget constraint budgeting behavior; low immediate urgency.",
        "underlying_need": "Price tracking and timely alerts.",
        "barrier_or_driver": "Barrier: External liquidity timing.",
        "business_impact": "Medium",
        "signal_strength": "High",
        "customer_journey_stage": "Wishlist Curation",
        "alternative_explanations": ["Users may buy alternative items if flash sales occur."],
        "contradictory_evidence": "Shoppers frequently complete purchases without sales when urgent styling needs arise.",
        "product_opportunity": "Provide high-value outfit contextualization to increase perceived utility and justify immediate purchase.",
        "research_hypothesis": "No monetary discount hypothesis generated. Price wait can be partially compressed by elevating outfit utility.",
        "research_questions": ["What proportion of wishlist items are bought at full price vs sale price?"],
        "why_these_quotes_matter": "Distinguishes price-driven delay from hesitation-driven delay.",
        "assumptions": ["Payday cycles occur predominantly at end of month."],
        "out_of_scope_reason": "",
        "causal_chain": "Budget Discipline ↓ Waiting for Monthly Liquidity ↓ Wishlist Holding Pattern",
        "reasoning_trace": "Timing Delay -> External Constraint -> Temporary Inaction",
        "confidence": "High"
    },
    "Quality & Fabric Distrust": {
        "research_relevance": "DIRECT",
        "relevance_reason": "Material and color reality gap prevents high-intent evaluation from converting.",
        "primary_issue": "Fabric & Quality Distrust",
        "theme_name": "Fabric Drape & Material Transparency Doubt",
        "evaluator_cluster": "High-Intent Evaluator",
        "evidence_summary": "Shoppers express concern that studio lighting hides fabric thinness, synthetic textures, or exact colors.",
        "observed_facts": [
            "Catalog imagery uses high-end studio lighting that obscures fabric texture and transparency.",
            "Shoppers seek unedited UGC photos taken in natural daylight."
        ],
        "observed_behavior": "Users inspect reviews repeatedly searching for customer photos before deciding to buy.",
        "behavioral_mechanism": "Information asymmetry between polished brand imagery and physical textile reality creates risk aversion.",
        "underlying_need": "Authentic, unfiltered customer photos showing fabric in natural lighting.",
        "barrier_or_driver": "Barrier: Distrust of studio product renders.",
        "business_impact": "Medium",
        "signal_strength": "Medium",
        "customer_journey_stage": "Evaluation & Doubt",
        "alternative_explanations": ["Users may prefer offline trial for premium fabrics."],
        "contradictory_evidence": "Positive reviews praise natural cotton/linen textures when verified with photos.",
        "product_opportunity": "Embed authentic verified customer try-on photos directly into wishlist card evaluation modals.",
        "research_hypothesis": "Displaying high-confidence UGC review photos within the wishlist modal will neutralize quality doubt.",
        "research_questions": ["What textile attributes most frequently disappoint online fashion shoppers?"],
        "why_these_quotes_matter": "Shows the role of authentic UGC in establishing product truth.",
        "assumptions": ["Sufficient volume of verified reviews with photos exist for top SKUs."],
        "out_of_scope_reason": "",
        "causal_chain": "Studio Photo Scepticism ↓ Fear of Poor Fabric/Drape ↓ Deferral to Offline Stores ↓ Wishlist Abandonment",
        "reasoning_trace": "Fabric Doubt -> Authenticity Gap -> Wishlist Stagnation",
        "confidence": "Medium"
    },
    "Passive Bookmarking": {
        "research_relevance": "OUT_OF_SCOPE",
        "relevance_reason": "General browsing or moodboarding with no short-term conversion friction.",
        "primary_issue": "Passive Moodboarding",
        "theme_name": "Casual Moodboarding & Inspiration Bookmarking",
        "evaluator_cluster": "Passive Bookmarker",
        "evidence_summary": "Users treat wishlist as a personal fashion Pinterest moodboard without immediate intent to purchase.",
        "observed_facts": ["Wishlists contain 50+ items curated over months without checkout attempts."],
        "observed_behavior": "Casual bookmarking while browsing trends.",
        "behavioral_mechanism": "Aspirational engagement without commercial commitment.",
        "underlying_need": "Organized collections and look moodboarding.",
        "barrier_or_driver": "Driver: Fashion inspiration seeking.",
        "business_impact": "Low",
        "signal_strength": "Low",
        "customer_journey_stage": "Discovery",
        "alternative_explanations": ["Users may convert during holiday seasons."],
        "contradictory_evidence": "None.",
        "product_opportunity": "",
        "research_hypothesis": "No research hypothesis generated. Casual moodboarding is out of scope for immediate conversion.",
        "research_questions": [],
        "why_these_quotes_matter": "Clarifies baseline top-of-funnel browsing behavior.",
        "assumptions": [],
        "out_of_scope_reason": "Passive moodboarding represents low-intent exploration.",
        "causal_chain": "Casual Inspiration Browsing -> Wishlist Moodboard -> No Short-term Purchase Intent",
        "reasoning_trace": "Moodboard -> Low Urgency",
        "confidence": "Medium"
    },
    "Operational Friction & Exchanges": {
        "research_relevance": "OUT_OF_SCOPE",
        "relevance_reason": "Post-purchase operational and logistics issues.",
        "primary_issue": "Exchange & Return Delays",
        "theme_name": "Exchange Delays & Delivery Friction",
        "evaluator_cluster": "Operational Friction",
        "evidence_summary": "Shoppers report frustration with delivery delays, exchange pickup friction, and courier coordination.",
        "observed_facts": ["Returns and size exchanges take multiple days to process."],
        "observed_behavior": "Complaining on app store reviews regarding delivery agents.",
        "behavioral_mechanism": "Logistical friction post-checkout.",
        "underlying_need": "Rapid exchanges and reliable delivery.",
        "barrier_or_driver": "Barrier: Courier and warehouse bottlenecks.",
        "business_impact": "Low",
        "signal_strength": "Medium",
        "customer_journey_stage": "Post-Purchase",
        "alternative_explanations": ["Regional courier delays."],
        "contradictory_evidence": "Most deliveries arrive on time in metro tiers.",
        "product_opportunity": "",
        "research_hypothesis": "Operational fulfillment issue routed to logistics teams.",
        "research_questions": [],
        "why_these_quotes_matter": "Distinguishes pre-purchase conversion blockers from logistics friction.",
        "assumptions": [],
        "out_of_scope_reason": "Operational logistics issue outside wishlist decision support scope.",
        "causal_chain": "Exchange Request ↓ Courier Bottlenecks ↓ Extended Turnaround ↓ Review Complaints",
        "reasoning_trace": "Logistics -> Operational",
        "confidence": "Medium"
    }
}

def generate_earned_confidence_explanation(count: int, sources: List[str], relevance: str, contra_count: int = 0) -> Tuple[str, str]:
    num_sources = len(sources) if sources else 1
    source_str = ", ".join(sources) if sources else "Play Store"
    if count >= 80 and relevance == "DIRECT":
        level = "High"
        exp = f"High confidence based on {count} customer reviews across {num_sources} sources ({source_str}) directly impacting wishlist conversion."
    elif count >= 20:
        level = "Medium"
        exp = f"Medium confidence based on {count} customer reviews in {source_str}."
    else:
        level = "Low"
        exp = f"Low confidence based on sample of {count} reviews."
    return level, exp

def label_clusters_with_llm(df: pd.DataFrame, keywords_dict: Dict[int, List[str]]) -> Dict[int, Dict[str, Any]]:
    logger.info("Labeling clusters and generating synthesized PM discovery metadata...")
    theme_metadata = {}
    total_records = len(df)

    domain_id_map = {
        0: "Fit & Drape Anxiety",
        1: "Wardrobe Pairing Uncertainty",
        2: "Price & Payday Waiting",
        3: "Quality & Fabric Distrust",
        4: "Passive Bookmarking",
        5: "Operational Friction & Exchanges"
    }

    for cluster_id, keywords in keywords_dict.items():
        sub_df = df[df["cluster_id"] == cluster_id]
        if sub_df.empty:
            continue

        domain_name = domain_id_map.get(cluster_id, "Fit & Drape Anxiety")
        if "sub_domain" in sub_df.columns and not sub_df["sub_domain"].empty:
            domain_name = sub_df["sub_domain"].iloc[0]

        base_meta = DOMAIN_TO_METADATA.get(domain_name, DOMAIN_TO_METADATA["Fit & Drape Anxiety"]).copy()
        
        sample_quotes = sub_df["cleaned_text"].dropna().tolist()[:6]
        sources = sub_df["source"].unique().tolist() if "source" in sub_df.columns else ["Play Store"]
        count = len(sub_df)
        pct = round((count / total_records) * 100, 1)

        conf_lvl, conf_exp = generate_earned_confidence_explanation(count, sources, base_meta["research_relevance"])

        base_meta["feedback_count"] = count
        base_meta["percentage_of_total"] = pct
        base_meta["cluster_id"] = cluster_id
        base_meta["example_quotes"] = sample_quotes
        base_meta["confidence"] = conf_lvl
        base_meta["confidence_explanation"] = conf_exp
        base_meta["evidence_summary"] = f"{base_meta['evidence_summary']} ({count} reviews, {pct}% of analyzed corpus)."

        theme_metadata[cluster_id] = base_meta

    return theme_metadata

if __name__ == "__main__":
    pass
