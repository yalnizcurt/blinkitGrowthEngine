import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from google_play_scraper import reviews, Sort
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_playstore_reviews(count: int = config.TARGET_PLAYSTORE_REVIEWS) -> List[Dict[str, Any]]:
    """
    Fetch reviews for Blinkit from Google Play Store.
    """
    logger.info(f"Fetching up to {count} reviews from Google Play Store for {config.PLAYSTORE_APP_ID}...")
    
    fetched_reviews = []
    # Fetch in batches of 200 using pagination token
    continuation_token = None
    batch_size = 200
    
    while len(fetched_reviews) < count:
        num_to_fetch = min(batch_size, count - len(fetched_reviews))
        try:
            result, continuation_token = reviews(
                config.PLAYSTORE_APP_ID,
                lang='en',
                country='in',
                sort=Sort.NEWEST,
                count=num_to_fetch,
                continuation_token=continuation_token
            )
            if not result:
                logger.info("No more reviews returned from Play Store.")
                break
                
            fetched_reviews.extend(result)
            logger.info(f"Fetched {len(fetched_reviews)} / {count} Play Store reviews...")
            
            if not continuation_token:
                break
        except Exception as e:
            logger.error(f"Error fetching Play Store reviews: {e}")
            break

    # Save raw json
    raw_path = config.RAW_DATA_DIR / "playstore_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        # Convert datetime objects to string for JSON serialization
        formatted = []
        for r in fetched_reviews:
            r_copy = r.copy()
            if "at" in r_copy and r_copy["at"]:
                r_copy["at"] = str(r_copy["at"])
            if "repliedAt" in r_copy and r_copy["repliedAt"]:
                r_copy["repliedAt"] = str(r_copy["repliedAt"])
            formatted.append(r_copy)
        json.dump(formatted, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Saved {len(fetched_reviews)} raw Play Store reviews to {raw_path}")
    return fetched_reviews

if __name__ == "__main__":
    fetch_playstore_reviews(count=500)
