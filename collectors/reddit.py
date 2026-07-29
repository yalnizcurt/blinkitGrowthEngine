import json
import logging
import time
import requests
from pathlib import Path
from typing import List, Dict, Any
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def fetch_pullpush_reddit(query: str, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Fetch live Reddit submissions and comments via PullPush archive API.
    Does not require Reddit API authentication.
    """
    results = []
    
    # 1. Fetch Submissions
    sub_url = "https://api.pullpush.io/reddit/search/submission/"
    params = {"q": query, "size": min(50, limit)}
    try:
        resp = requests.get(sub_url, params=params, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            for item in data:
                title = item.get("title", "")
                selftext = item.get("selftext", "")
                full_text = f"{title}\n{selftext}".strip()
                if len(full_text) > 15:
                    results.append({
                        "id": f"sub_{item.get('id', '')}",
                        "subreddit": item.get("subreddit", ""),
                        "text": full_text,
                        "score": item.get("score", 0),
                        "url": item.get("full_link", f"https://reddit.com/r/{item.get('subreddit')}/comments/{item.get('id')}"),
                        "created_utc": item.get("created_utc", 0),
                        "type": "post"
                    })
    except Exception as e:
        logger.warning(f"PullPush submission fetch error for query '{query}': {e}")

    # 2. Fetch Comments
    comment_url = "https://api.pullpush.io/reddit/search/comment/"
    try:
        resp = requests.get(comment_url, params=params, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            for item in data:
                body = item.get("body", "").strip()
                if len(body) > 20 and body != "[deleted]" and body != "[removed]":
                    results.append({
                        "id": f"com_{item.get('id', '')}",
                        "subreddit": item.get("subreddit", ""),
                        "text": body,
                        "score": item.get("score", 0),
                        "url": f"https://reddit.com{item.get('permalink', '')}",
                        "created_utc": item.get("created_utc", 0),
                        "type": "comment"
                    })
    except Exception as e:
        logger.warning(f"PullPush comment fetch error for query '{query}': {e}")

    return results

def fetch_reddit_discussions() -> List[Dict[str, Any]]:
    """
    Fetch Reddit discussions for Blinkit using live archive scrapers.
    """
    logger.info("Fetching live Reddit discussions for Blinkit & Quick Commerce via PullPush...")
    all_reddit_data = []
    seen_ids = set()

    for term in config.REDDIT_SEARCH_TERMS:
        logger.info(f"Querying PullPush Reddit for '{term}'...")
        items = fetch_pullpush_reddit(query=term, limit=30)
        for item in items:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                all_reddit_data.append(item)
        time.sleep(1.0)

    raw_path = config.RAW_DATA_DIR / "reddit_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_reddit_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(all_reddit_data)} raw live Reddit posts/comments to {raw_path}")
    return all_reddit_data

if __name__ == "__main__":
    fetch_reddit_discussions()
