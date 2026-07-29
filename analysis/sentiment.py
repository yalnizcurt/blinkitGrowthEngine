import logging
import pandas as pd
from typing import Dict, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic lexicon-assisted sentiment helper for scale & speed
POSITIVE_WORDS = set(['love', 'great', 'good', 'fast', 'convenient', 'super', 'best', 'easy', 'fresh', 'amazing', 'excellent', 'useful'])
NEGATIVE_WORDS = set(['bad', 'worst', 'expensive', 'costly', 'slow', 'dirty', 'stale', 'damaged', 'useless', 'cheated', 'poor', 'issue', 'problem', 'hate'])

def compute_review_sentiment(text: str, rating: float = None) -> str:
    """
    Determine review sentiment based on rating and text words.
    """
    if rating is not None and not pd.isna(rating) and rating > 0:
        if rating >= 4:
            return "positive"
        elif rating <= 2:
            return "negative"

    text_lower = text.lower()
    words = set(text_lower.split())
    
    pos_count = len(words.intersection(POSITIVE_WORDS))
    neg_count = len(words.intersection(NEGATIVE_WORDS))

    if pos_count > neg_count and pos_count > 0:
        return "positive"
    elif neg_count > pos_count and neg_count > 0:
        return "negative"
    elif pos_count > 0 and neg_count > 0:
        return "mixed"
    return "neutral"

def analyze_cluster_sentiments(df: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
    """
    Compute aggregate sentiment metrics and distribution per cluster.
    """
    df["sentiment"] = df.apply(lambda r: compute_review_sentiment(r["cleaned_text"], r.get("rating")), axis=1)

    cluster_sentiments = {}
    for c_id in df["cluster_id"].unique():
        if c_id == -1:
            continue
        c_df = df[df["cluster_id"] == c_id]
        total = len(c_df)
        counts = c_df["sentiment"].value_counts().to_dict()
        
        pos_pct = round((counts.get("positive", 0) / total) * 100, 1)
        neg_pct = round((counts.get("negative", 0) / total) * 100, 1)
        neu_pct = round((counts.get("neutral", 0) / total) * 100, 1)
        mix_pct = round((counts.get("mixed", 0) / total) * 100, 1)

        # Dominant
        dominant = max(counts, key=counts.get) if counts else "neutral"

        cluster_sentiments[int(c_id)] = {
            "dominant_sentiment": dominant,
            "distribution": {
                "positive": pos_pct,
                "negative": neg_pct,
                "neutral": neu_pct,
                "mixed": mix_pct
            },
            "summary_string": f"{dominant} ({neg_pct}% negative, {pos_pct}% positive, {neu_pct}% neutral)"
        }

    return cluster_sentiments

if __name__ == "__main__":
    pass
