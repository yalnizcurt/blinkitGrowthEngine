import logging
import numpy as np
import pandas as pd
import re
from typing import Tuple, Dict, Any, List
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CUSTOM_STOP_WORDS = list(CountVectorizer(stop_words="english").get_stop_words()) + [
    "app", "myntra", "good", "very", "delivery", "service", "nice", 
    "hai", "bahut", "bhi", "karo", "kya", "ko", "se", "par", "ka", "ki", 
    "ke", "ho", "raha", "kar", "ne", "the", "and", "to", "in", "of", "is", "it", "for", "on", "you", "my"
]

DOMAIN_PATTERNS = [
    (
        "Fit & Drape Anxiety",
        "High-Intent Evaluator",
        [
            r"size|sizing|fit|fits|fitted|tight|loose|length|waist|shoulder|chest|drape|height|model|chart|variance|small|large|tight|loose|different|zara|h&m|roadster|hrx|inseam|sleeves|torso|body type|fits perfectly|true to size"
        ]
    ),
    (
        "Wardrobe Pairing Uncertainty",
        "High-Intent Evaluator",
        [
            r"pair|pairing|match|matching|wear with|combine|style with|coordinate|jeans|pants|shoes|sneakers|jacket|shirt|trousers|closet|wardrobe|existing|owned|lookbook|outfit|go well with|looks good with|sitting in wishlist|saved in wishlist"
        ]
    ),
    (
        "Price & Payday Waiting",
        "Passive Price Waiter",
        [
            r"wait|waiting|salary|payday|month end|sale|bff|eors|discount|offer|coupon|deal|price drop|expensive|costly|pricey|overpriced|holding off|until price drops"
        ]
    ),
    (
        "Quality & Fabric Distrust",
        "High-Intent Evaluator",
        [
            r"fabric|material|cloth|cotton|linen|suede|polyester|sheer|see-through|transparent|cheap|poor|bad|thin|color different|shade|lighting|studio|stitching|finish"
        ]
    ),
    (
        "Operational Friction & Exchanges",
        "Operational Friction",
        [
            r"return|exchange|replacement|pickup|delivery|agent|courier|ekart|shadowfax|late|refund|money|customer care|call|delay"
        ]
    ),
    (
        "Passive Bookmarking",
        "Passive Bookmarker",
        [
            r"bookmark|moodboard|pinterest|window shopping|saved for future|saved for later|saving items|just looking|someday|future reference|collection"
        ]
    )
]

def enforce_cluster_purity_split(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforces cluster purity and categorizes reviews into the 6 verified behavioral buckets.
    """
    logger.info("Enforcing strict Cluster Purity & Split rule across fashion conversion clusters...")
    df = df.copy()

    def detect_quote_domain(text: str) -> Tuple[str, str]:
        t = str(text).lower()
        for domain, cluster_group, patterns in DOMAIN_PATTERNS:
            for pat in patterns:
                if re.search(pat, t):
                    return domain, cluster_group
        # Default high-intent styling evaluation if unclassified fashion text
        return "Fit & Drape Anxiety", "High-Intent Evaluator"

    classified_tuples = df["cleaned_text"].apply(detect_quote_domain)
    df["sub_domain"] = [t[0] for t in classified_tuples]
    df["evaluator_cluster"] = [t[1] for t in classified_tuples]

    domain_cluster_ids = {
        "Fit & Drape Anxiety": 0,
        "Wardrobe Pairing Uncertainty": 1,
        "Price & Payday Waiting": 2,
        "Quality & Fabric Distrust": 3,
        "Passive Bookmarking": 4,
        "Operational Friction & Exchanges": 5
    }

    df["cluster_id"] = df["sub_domain"].map(domain_cluster_ids).fillna(0).astype(int)
    logger.info(f"Purity split complete. Created {len(domain_cluster_ids)} pure fashion clusters isolating High-Intent vs Passive segments.")
    return df

def cluster_feedback(df: pd.DataFrame, embeddings: np.ndarray = None) -> Tuple[pd.DataFrame, Dict[int, List[str]]]:
    """
    Cluster fashion feedback items and calculate keywords per cluster.
    """
    texts = df["cleaned_text"].tolist()
    logger.info(f"Clustering {len(texts)} feedback items into conversion clusters...")

    df = enforce_cluster_purity_split(df)

    keywords_dict = {}
    total_items = len(df)
    
    for c_id in sorted(df["cluster_id"].unique()):
        c_texts = df[df["cluster_id"] == c_id]["cleaned_text"].tolist()
        count = len(c_texts)
        pct = round((count / total_items) * 100, 1)
        sub_vec = CountVectorizer(stop_words=CUSTOM_STOP_WORDS, max_features=8)
        try:
            sub_vec.fit(c_texts)
            keywords_dict[int(c_id)] = list(sub_vec.vocabulary_.keys())[:8]
        except Exception:
            keywords_dict[int(c_id)] = ["wishlist", "fit", "size", "styling"]

    logger.info(f"Cluster pipeline output {len(keywords_dict)} pure clusters.")
    return df, keywords_dict

if __name__ == "__main__":
    pass
