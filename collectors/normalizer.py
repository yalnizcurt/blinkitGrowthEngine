import json
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_raw_data() -> List[Dict[str, Any]]:
    """
    Load raw JSON data from all three collectors.
    """
    unified_records = []

    # Play Store
    playstore_file = config.RAW_DATA_DIR / "playstore_raw.json"
    if playstore_file.exists():
        with open(playstore_file, "r", encoding="utf-8") as f:
            ps_data = json.load(f)
            for item in ps_data:
                unified_records.append({
                    "id": f"ps_{item.get('reviewId', '')}",
                    "source": "play_store",
                    "text": str(item.get("content", "")).strip(),
                    "rating": item.get("score", 0),
                    "date": str(item.get("at", "")),
                    "upvotes": item.get("thumbsUpCount", 0),
                    "url": f"https://play.google.com/store/apps/details?id={config.PLAYSTORE_APP_ID}"
                })

    # App Store
    appstore_file = config.RAW_DATA_DIR / "appstore_raw.json"
    if appstore_file.exists():
        with open(appstore_file, "r", encoding="utf-8") as f:
            as_data = json.load(f)
            for idx, item in enumerate(as_data):
                unified_records.append({
                    "id": f"as_{item.get('review_id', idx)}",
                    "source": "app_store",
                    "text": str(item.get("review", "")).strip(),
                    "rating": item.get("rating", 0),
                    "date": str(item.get("date", "")),
                    "upvotes": 0,
                    "url": f"https://apps.apple.com/in/app/id{config.APPSTORE_APP_ID}"
                })

    # Reddit
    reddit_file = config.RAW_DATA_DIR / "reddit_raw.json"
    if reddit_file.exists():
        with open(reddit_file, "r", encoding="utf-8") as f:
            rd_data = json.load(f)
            for item in rd_data:
                unified_records.append({
                    "id": f"rd_{item.get('id', '')}",
                    "source": "reddit",
                    "text": str(item.get("text", "")).strip(),
                    "rating": None,
                    "date": str(item.get("created_utc", "")),
                    "upvotes": item.get("score", 0),
                    "url": item.get("url", "")
                })

    logger.info(f"Loaded a total of {len(unified_records)} records across Play Store, App Store, and Reddit.")
    return unified_records

def normalize_dataset() -> pd.DataFrame:
    """
    Combine all raw datasets, drop empty texts, and save to unified CSV.
    """
    records = load_raw_data()
    if not records:
        logger.warning("No raw data records found to normalize.")
        df = pd.DataFrame(columns=["id", "source", "text", "rating", "date", "upvotes", "url"])
    else:
        df = pd.DataFrame(records)
        df = df[df["text"].str.len() > 10].copy()
        df.drop_duplicates(subset=["text"], inplace=True)
        
    df.to_csv(config.UNIFIED_CSV, index=False)
    logger.info(f"Saved unified dataset ({len(df)} rows) to {config.UNIFIED_CSV}")
    return df

if __name__ == "__main__":
    normalize_dataset()
