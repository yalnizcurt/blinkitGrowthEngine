import logging
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_embeddings(texts: list) -> np.ndarray:
    """
    Generate vector embeddings using SentenceTransformers.
    """
    logger.info(f"Loading embedding model '{config.EMBEDDING_MODEL}'...")
    model = SentenceTransformer(config.EMBEDDING_MODEL)
    
    logger.info(f"Encoding {len(texts)} text items into dense vector embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    
    logger.info(f"Generated embeddings matrix with shape: {embeddings.shape}")
    return embeddings

if __name__ == "__main__":
    test_texts = ["Love buying fresh veggies on Blinkit", "Reordering milk every morning is super easy"]
    embs = generate_embeddings(test_texts)
    print("Shape:", embs.shape)
