import json
import logging
import time
import random
import requests
from pathlib import Path
from typing import List, Dict, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- STRATEGY A: app-store-scraper library ----

def fetch_via_library(count: int) -> List[Dict[str, Any]]:
    """
    Primary strategy: use the app-store-scraper pip package.
    Returns a list of review dicts, or raises on failure.
    """
    from app_store_scraper import AppStore

    logger.info(f"[Strategy A] Using app-store-scraper library for app_id={config.APPSTORE_APP_ID}, country={config.APPSTORE_COUNTRY}")

    app = AppStore(
        country=config.APPSTORE_COUNTRY,
        app_name=config.APPSTORE_APP_NAME,
        app_id=str(config.APPSTORE_APP_ID)
    )

    app.review(how_many=count, sleep=random.uniform(1.0, 3.0))

    reviews_list = []
    for r in app.reviews:
        title = r.get("title", "")
        review_text = r.get("review", "")
        full_text = f"{title} - {review_text}" if title and review_text else (review_text or title)
        
        date_val = r.get("date", "")
        if hasattr(date_val, "isoformat"):
            date_val = date_val.isoformat()

        if full_text.strip():
            reviews_list.append({
                "userName": r.get("userName", ""),
                "review": full_text.strip(),
                "rating": int(r.get("rating", 0)),
                "date": str(date_val),
                "review_id": str(r.get("id", ""))
            })

    logger.info(f"[Strategy A] Fetched {len(reviews_list)} reviews via app-store-scraper library.")
    return reviews_list


# ---- STRATEGY B: Hardened iTunes RSS JSON ----

RSS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://apps.apple.com/",
}

def fetch_via_rss(count: int) -> List[Dict[str, Any]]:
    """
    Fallback strategy: iTunes RSS JSON endpoint with retry and realistic headers.
    """
    reviews_list = []
    max_pages = min(10, max(1, count // 50))

    for page in range(1, max_pages + 1):
        url = f"https://itunes.apple.com/{config.APPSTORE_COUNTRY}/rss/customerreviews/page={page}/id={config.APPSTORE_APP_ID}/sortBy=mostRecent/json"

        success = False
        for attempt in range(3):
            try:
                delay = random.uniform(1.0, 3.0) * (attempt + 1)
                time.sleep(delay)

                resp = requests.get(
                    url,
                    timeout=15,
                    headers=RSS_HEADERS,
                    verify=True  # Try with SSL first
                )

                if resp.status_code == 403:
                    logger.warning(f"[Strategy B] Page {page}: 403 Forbidden. Apple may be rate-limiting.")
                    break
                if resp.status_code != 200:
                    logger.warning(f"[Strategy B] Page {page}: HTTP {resp.status_code}, attempt {attempt+1}")
                    continue

                data = resp.json()
                feed = data.get("feed", {})
                entries = feed.get("entry", [])
                if not entries:
                    logger.info(f"[Strategy B] Page {page}: No entries found. Stopping pagination.")
                    success = True
                    break

                page_count = 0
                for entry in entries:
                    if isinstance(entry, dict) and "im:name" in entry:
                        continue  # This is the app metadata entry, skip it
                    if not isinstance(entry, dict):
                        continue

                    r_id = entry.get("id", {}).get("label", "")
                    title = entry.get("title", {}).get("label", "")
                    text = entry.get("content", {}).get("label", "")
                    rating = 0
                    if "im:rating" in entry:
                        try:
                            rating = int(entry["im:rating"]["label"])
                        except (ValueError, KeyError, TypeError):
                            pass
                    author = entry.get("author", {}).get("name", {}).get("label", "")

                    full_text = f"{title} - {text}" if title and text else (text or title)
                    if full_text.strip():
                        reviews_list.append({
                            "userName": author,
                            "review": full_text.strip(),
                            "rating": rating,
                            "date": "",
                            "review_id": r_id
                        })
                        page_count += 1

                logger.info(f"[Strategy B] Page {page}: fetched {page_count} reviews.")
                success = True
                break

            except requests.exceptions.SSLError:
                logger.warning(f"[Strategy B] SSL error on page {page}, retrying with verify=False")
                try:
                    resp = requests.get(url, timeout=15, headers=RSS_HEADERS, verify=False)
                    if resp.status_code == 200:
                        data = resp.json()
                        entries = data.get("feed", {}).get("entry", [])
                        for entry in entries:
                            if isinstance(entry, dict) and "im:name" in entry:
                                continue
                            if not isinstance(entry, dict):
                                continue
                            r_id = entry.get("id", {}).get("label", "")
                            title = entry.get("title", {}).get("label", "")
                            text = entry.get("content", {}).get("label", "")
                            rating = 0
                            if "im:rating" in entry:
                                try:
                                    rating = int(entry["im:rating"]["label"])
                                except (ValueError, KeyError, TypeError):
                                    pass
                            author = entry.get("author", {}).get("name", {}).get("label", "")
                            full_text = f"{title} - {text}" if title and text else (text or title)
                            if full_text.strip():
                                reviews_list.append({
                                    "userName": author,
                                    "review": full_text.strip(),
                                    "rating": rating,
                                    "date": "",
                                    "review_id": r_id
                                })
                        success = True
                        break
                except Exception as e2:
                    logger.warning(f"[Strategy B] SSL fallback also failed: {e2}")

            except Exception as e:
                logger.warning(f"[Strategy B] Page {page}, attempt {attempt+1}: {e}")
                time.sleep(2 * (attempt + 1))

        if not success and resp.status_code == 403:
            break

    logger.info(f"[Strategy B] Total fetched via RSS: {len(reviews_list)} reviews.")
    return reviews_list


# ---- MAIN ENTRY POINT ----

def fetch_appstore_reviews(count: int = config.TARGET_APPSTORE_REVIEWS) -> List[Dict[str, Any]]:
    """
    Fetch reviews for Blinkit from Apple App Store.
    Uses Strategy A (library) first; falls back to Strategy B (RSS) on failure.
    """
    logger.info(f"Fetching up to {count} reviews from Apple App Store for ID {config.APPSTORE_APP_ID}...")

    fetched_reviews = []

    # Strategy A: app-store-scraper library
    try:
        fetched_reviews = fetch_via_library(count)
    except Exception as e:
        logger.warning(f"[Strategy A] Failed: {e}. Falling back to Strategy B (RSS).")

    # Strategy B fallback if A returned nothing
    if len(fetched_reviews) == 0:
        logger.info("Strategy A returned 0 reviews. Trying Strategy B (RSS)...")
        try:
            fetched_reviews = fetch_via_rss(count)
        except Exception as e:
            logger.error(f"[Strategy B] Also failed: {e}")

    # If both failed, try US country as last resort
    if len(fetched_reviews) == 0:
        logger.info("Both strategies returned 0 for India. Trying US App Store as last resort...")
        original_country = config.APPSTORE_COUNTRY
        try:
            config.APPSTORE_COUNTRY = "us"
            fetched_reviews = fetch_via_rss(count)
        except Exception as e:
            logger.error(f"US fallback also failed: {e}")
        finally:
            config.APPSTORE_COUNTRY = original_country

    logger.info(f"Total App Store reviews fetched: {len(fetched_reviews)}")

    raw_path = config.RAW_DATA_DIR / "appstore_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(fetched_reviews, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(fetched_reviews)} raw App Store reviews to {raw_path}")
    return fetched_reviews


if __name__ == "__main__":
    reviews = fetch_appstore_reviews(count=500)
    print(f"\nDone. Fetched {len(reviews)} App Store reviews.")
    if reviews:
        print(f"Sample: [{reviews[0].get('rating')}] {reviews[0].get('review','')[:150]}")
