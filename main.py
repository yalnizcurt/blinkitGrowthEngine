import sys
import logging
import pandas as pd
from typing import List, Optional
import config

from collectors.playstore import fetch_playstore_reviews
from collectors.appstore import fetch_appstore_reviews
from collectors.reddit import fetch_reddit_discussions
from collectors.normalizer import normalize_dataset
from preprocessing.cleaner import preprocess_and_deduplicate
from preprocessing.noise_filter import filter_dataset
from analysis.embeddings import generate_embeddings
from analysis.clustering import cluster_feedback
from analysis.labeler import label_clusters_with_llm
from analysis.sentiment import analyze_cluster_sentiments
from analysis.scorer import score_and_prioritize_themes
from analysis.rigorous_extraction import extract_rigorous_themes
from output.question_generator import generate_insights_and_questions
from output.exporter import export_all_formats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("MyntraOpportunityEngine")

def run_pipeline(
    playstore_count: Optional[int] = None,
    appstore_count: Optional[int] = None,
    reddit_terms: Optional[List[str]] = None,
    sources: Optional[List[str]] = None
):
    logger.info("==================================================")
    logger.info("   MYNTRA OPPORTUNITY DISCOVERY ENGINE PIPELINE   ")
    logger.info("   Target: 30-Day Wishlist-to-Purchase Conversion  ")
    logger.info("==================================================")

    target_sources = sources if sources else ["playstore", "appstore", "reddit"]
    ps_count = playstore_count if playstore_count is not None else config.TARGET_PLAYSTORE_REVIEWS
    as_count = appstore_count if appstore_count is not None else config.TARGET_APPSTORE_REVIEWS

    # Step 1: Data Collection
    logger.info("--- PHASE 1: DATA COLLECTION ---")
    if "playstore" in target_sources:
        try:
            logger.info(f"Fetching {ps_count} reviews from Play Store for com.myntra.android...")
            fetch_playstore_reviews(count=ps_count)
        except Exception as e:
            logger.error(f"Play Store fetch error: {e}")

    if "appstore" in target_sources:
        try:
            logger.info(f"Fetching {as_count} reviews from App Store...")
            fetch_appstore_reviews(count=as_count)
        except Exception as e:
            logger.error(f"App Store fetch error: {e}")

    if "reddit" in target_sources:
        try:
            terms = reddit_terms if reddit_terms else config.REDDIT_SEARCH_TERMS
            logger.info(f"Fetching live Reddit fashion discussions: {terms}...")
            fetch_reddit_discussions()
        except Exception as e:
            logger.error(f"Reddit fetch error: {e}")

    # Step 2: Normalization & Preprocessing
    logger.info("--- PHASE 2: NORMALIZATION & PREPROCESSING ---")
    unified_df = normalize_dataset()
    if unified_df.empty:
        logger.error("Unified dataset is empty! Aborting pipeline.")
        return

    cleaned_df = preprocess_and_deduplicate(unified_df)
    filtered_df = filter_dataset(cleaned_df)

    if filtered_df.empty:
        logger.warning("Filtered behavioral dataset is empty! Using cleaned dataset as fallback.")
        filtered_df = cleaned_df

    logger.info(f"High-signal fashion feedback items to process: {len(filtered_df)}")

    # Step 3: Rigorous Theme Extraction
    logger.info("--- PHASE 3: RIGOROUS BEHAVIORAL TAXONOMY EXTRACTION ---")
    rigorous_results = extract_rigorous_themes(config.FILTERED_CSV)

    # Step 4: Embeddings & Clustering (Isolating High-Intent Evaluators)
    logger.info("--- PHASE 4: NLP EMBEDDINGS & CLUSTERING ---")
    texts = filtered_df["cleaned_text"].tolist()
    embeddings = generate_embeddings(texts)
    clustered_df, keywords_dict = cluster_feedback(filtered_df, embeddings)

    # Step 5: Theme Labeling & Sentiment
    logger.info("--- PHASE 5: THEME SYNTHESIS & SENTIMENT ANALYSIS ---")
    theme_metadata = label_clusters_with_llm(clustered_df, keywords_dict)
    cluster_sentiments = analyze_cluster_sentiments(clustered_df)

    # Step 6: Scoring & Prioritization
    logger.info("--- PHASE 6: SCORING & PRIORITIZATION ENGINE ---")
    scored_themes = score_and_prioritize_themes(clustered_df, theme_metadata, cluster_sentiments)

    # Step 7: Insight & Question Generation
    logger.info("--- PHASE 7: INSIGHT HYPOTHESIS & RESEARCH QUESTION GENERATION ---")
    final_themes = generate_insights_and_questions(scored_themes)

    # Step 8: Export
    logger.info("--- PHASE 8: EXPORTING ARTIFACTS ---")
    output_paths = export_all_formats(final_themes, total_feedback_count=len(filtered_df))

    logger.info("==================================================")
    logger.info("   PIPELINE COMPLETED SUCCESSFULLY!              ")
    logger.info(f"   Rigorous JSON:   {config.RIGOROUS_RESULTS_JSON}")
    logger.info(f"   CSV Output:      {output_paths['csv']}")
    logger.info(f"   JSON Output:     {output_paths['json']}")
    logger.info(f"   Markdown Summary:{output_paths['markdown']}")
    logger.info("==================================================")
    return output_paths

if __name__ == "__main__":
    run_pipeline()
