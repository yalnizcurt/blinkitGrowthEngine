import re
import logging
import pandas as pd
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NSFW, Spam, Bot, and Promotional patterns to drop immediately
SPAM_NSFW_PATTERNS = [
    r'\b(onlyfans|nsfw|porn|sex|nude|nudes|escort|camgirl|erotic|boobs|tits|xrated|xxx|adult)\b',
    r'\b(crypto|bitcoin|eth|airdrop|binance|telegram|t\.me\/|wa\.me\/|whatsapp group|free money|earn \$\d+)\b',
    r'\b(promo code|referral code|use my code|discount code|cashback app|free recharge|task pay|betting|casino)\b',
    r'\b(subscribers|follow me|check out my channel|youtube\.com|instagram\.com)\b'
]

def clean_text(text: str) -> str:
    """
    Clean individual review text.
    """
    if not isinstance(text, str):
        return ""
    # Remove control characters & newlines
    text = re.sub(r'[\r\n\t]+', ' ', text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_spam_or_nsfw(text: str) -> bool:
    """
    Check if text contains NSFW keywords, spam, or promotional copy.
    """
    text_lower = text.lower()
    for pattern in SPAM_NSFW_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def preprocess_and_deduplicate(df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Clean text, filter short noise, remove NSFW/spam, and deduplicate.
    """
    if df is None:
        if not config.UNIFIED_CSV.exists():
            raise FileNotFoundError(f"{config.UNIFIED_CSV} does not exist.")
        df = pd.read_csv(config.UNIFIED_CSV)

    logger.info(f"Starting cleaning on {len(df)} initial rows...")

    # Apply text cleaning
    df["cleaned_text"] = df["text"].apply(clean_text)

    # Filter short noise (< 20 chars)
    df = df[df["cleaned_text"].str.len() >= 20].copy()

    # Filter NSFW and Spam
    df = df[~df["cleaned_text"].apply(is_spam_or_nsfw)].copy()

    # Deduplicate exact text
    df.drop_duplicates(subset=["cleaned_text"], inplace=True)

    logger.info(f"Cleaned dataset reduced to {len(df)} unique quality rows (spam & NSFW removed).")
    return df

if __name__ == "__main__":
    df = preprocess_and_deduplicate()
    print(f"Cleaned sample rows: {len(df)}")
