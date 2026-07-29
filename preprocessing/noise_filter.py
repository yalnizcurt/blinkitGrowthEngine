import re
import logging
import pandas as pd
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keywords for pure noise (logistics/bugs/generic praise/nsfw)
PURE_NOISE_PATTERNS = [
    # Delivery complaints without behavioral context
    r'\b(late delivery|delivery boy|delivery person|delivery guy|delivery driver|delayed delivery|rider|delivery delay|slow delivery|delivery agent)\b',
    # Technical bugs/payment issues
    r'\b(app crash|app freezing|login issue|otp not coming|payment failed|money deducted|refund pending|server error|update app|buggy app)\b',
    # Generic short praise/complaint
    r'^(great app|good app|super app|best app|nice app|worst app|bad app|useless app|fraud app|scam app|very good|awesome|superb|love this app|nice delivery|payment issue)[\s!\.]*$',
    # Spam/NSFW/Bot residual patterns
    r'\b(onlyfans|nsfw|porn|subscribers|crypto|promo code|cashback app|referral code)\b'
]

# Keywords indicating high behavioral signal
BEHAVIORAL_SIGNAL_PATTERNS = [
    r'\b(buy|order|purchase|try|tried|trying|category|categories|item|items|product|products|vegetable|vegetables|fruit|fruits|grocery|groceries|meat|dairy|beauty|electronics|apparel)\b',
    r'\b(habit|habitual|always buy|reorder|frequently|daily|weekly|routine|substitute|brand|options|variety|selection|discover|exploration|explore|search|recommend|suggestion)\b',
    r'\b(price|expensive|cheap|discount|offer|margin|quality|fresh|freshness|trust|hesitate|hesitation|reluctant|doubt|confidence|expire|expiry|damage)\b',
    r'\b(offline|store|supermarket|zepto|instamart|bigbasket|amazon|comparison|compare|switch|switched)\b'
]

def is_pure_noise(text: str) -> bool:
    """
    Check if a text is purely operational/technical noise or spam.
    """
    text_lower = text.lower()

    # Drop if spam or NSFW
    if any(re.search(p, text_lower) for p in [r'\b(onlyfans|nsfw|porn|subscribers|crypto|promo code|referral)\b']):
        return True

    # If text contains clear behavioral signals, keep it
    for pattern in BEHAVIORAL_SIGNAL_PATTERNS:
        if re.search(pattern, text_lower):
            return False

    # If text matches pure noise patterns and has no behavioral terms, drop it
    for pattern in PURE_NOISE_PATTERNS:
        if re.search(pattern, text_lower):
            return True

    return False

def filter_dataset(df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Filter noise out of the dataset and save the clean behavioral dataset to config.FILTERED_CSV.
    """
    if df is None:
        if not config.UNIFIED_CSV.exists():
            raise FileNotFoundError(f"{config.UNIFIED_CSV} does not exist.")
        df = pd.read_csv(config.UNIFIED_CSV)

    if "cleaned_text" not in df.columns:
        df["cleaned_text"] = df["text"].astype(str)

    initial_count = len(df)
    logger.info(f"Filtering noise & spam from {initial_count} records...")

    df["is_noise"] = df["cleaned_text"].apply(is_pure_noise)
    filtered_df = df[~df["is_noise"]].copy()
    filtered_df.drop(columns=["is_noise"], inplace=True)

    filtered_df.to_csv(config.FILTERED_CSV, index=False)
    logger.info(f"Retained {len(filtered_df)} / {initial_count} high-signal behavioral records in {config.FILTERED_CSV}")
    return filtered_df

if __name__ == "__main__":
    filter_dataset()
