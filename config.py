import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
RESULTS_DATA_DIR = DATA_DIR / "results"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# App Identifiers
PLAYSTORE_APP_ID = "com.myntra.android"
APPSTORE_APP_NAME = "myntra-fashion-shopping-app"
APPSTORE_APP_ID = 907394059
APPSTORE_COUNTRY = "in"

# Scraping Targets
TARGET_PLAYSTORE_REVIEWS = 2500
TARGET_APPSTORE_REVIEWS = 1000
PLAYSTORE_KEYWORDS = ["wishlist", "saved", "size", "fit", "looks like", "matching", "pair", "fabric", "quality", "return"]
REDDIT_SUBREDDITS = ["IndianFashionAddicts", "Myntra", "IndianBeautyDeals"]
REDDIT_SEARCH_TERMS = ["Myntra sizing", "Myntra fit", "pair with", "what to wear with", "wishlist sitting"]

# LLM Configuration (Groq AI Engine)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_API_KEY = (
    os.getenv("GROQ_API_KEY") or
    GROQ_API_KEY or
    os.getenv("OPENAI_API_KEY") or
    os.getenv("LLM_API_KEY") or
    ""
)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

# Clustering Parameters
MIN_TOPIC_SIZE = 15
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Output Paths
UNIFIED_CSV = CLEANED_DATA_DIR / "unified_reviews.csv"
FILTERED_CSV = CLEANED_DATA_DIR / "filtered_reviews.csv"
FINAL_RESULTS_CSV = RESULTS_DATA_DIR / "insight_engine_results.csv"
FINAL_RESULTS_JSON = RESULTS_DATA_DIR / "insight_engine_results.json"
RIGOROUS_RESULTS_JSON = RESULTS_DATA_DIR / "rigorous_theme_extraction.json"
FINAL_SUMMARY_MD = RESULTS_DATA_DIR / "insight_engine_summary.md"
