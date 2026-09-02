import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_embeddings(texts: list) -> np.ndarray:
    """
    Generate vector embeddings with SentenceTransformers if available, or fast TF-IDF fallback.
    """
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model '{config.EMBEDDING_MODEL}'...")
        model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info(f"Encoding {len(texts)} text items into dense vector embeddings...")
        embeddings = model.encode(texts, show_progress_bar=False, batch_size=64)
        return np.array(embeddings)
    except Exception as e:
        logger.info(f"Using fast TfidfVectorizer embeddings: {e}")
        tfidf = TfidfVectorizer(max_features=256, stop_words="english")
        return tfidf.fit_transform(texts).toarray()

if __name__ == "__main__":
    test_texts = ["Love buying Roadster jackets on Myntra", "Sizing is confusing across brands"]
    embs = generate_embeddings(test_texts)
    print("Shape:", embs.shape)
