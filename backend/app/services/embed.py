import os
import time
import requests
import numpy as np
from dotenv import load_dotenv

### Set up configs
from app.configs.config import (
    LOCAL_DEPLOYMENT,
    ENCODER
)

### Set up logger for model logs
from app.logging import setup_logger
logger = setup_logger(__name__)
load_dotenv()

# API encoder
HF_API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{ENCODER}"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

# Local encoder
_encoder = None

async def _get_encoder():
    """Lazily load encoder on first call, then reuse"""
    global _encoder
    if _encoder is not None:
        return _encoder
    
    logger.info("Setting up encoder")
    from sentence_transformers import SentenceTransformer
    _encoder = SentenceTransformer(ENCODER)
    logger.info("Encoder downloaded")
    
    return _encoder


async def encoder_warm_up():
    """Pre-load the encoder into memory during application startup before first call"""
    logger.info("Warming up encoder...")
    await _get_encoder()
    logger.info("Encoder warm-up complete")


def local_embed(concepts):
    """Generates embedding using local encoder

    Input:
    
    Output:
    """
    model = _get_encoder()
    embeddings = model.encode(
        concepts,
        convert_to_numpy=True
    )
    return embeddings.tolist()


def api_embed(concepts):
    """Generates embedding using API encoder

    Input:
    
    Output:
    """
    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json={
                "inputs": concepts,
                "options": {"wait_for_model": True}
            },
            timeout=30
        )
        result = response.json()

        if isinstance(result, dict) and "error" in result:
            logger.error(f"HF Embedding API error: {result['error']}")
            raise RuntimeError(f"HF Embedding API error: {result['error']}")

        embeddings = []
        for item in result:
            arr = np.array(item)
            if arr.ndim == 2:
                arr = arr.mean(axis=0) 
            embeddings.append(arr.tolist())

        return embeddings

    except Exception as e:
        logger.error(f"HF Embedding API request failed: {e}")
        raise


async def generate_embeddings(concepts: list[str]):
    """Embeds concepts using preset encoder 

    Input:

    Ouput:
    """
    start = time.time()

    if LOCAL_DEPLOYMENT:
        import asyncio
        embeddings = await asyncio.to_thread(local_embed, concepts)
    else:
        embeddings = api_embed(concepts)

    logger.info(
        f"Embeddings generated for {len(concepts)} concept(s) "
        f"in {round(time.time() - start, 2)}s"
    )
    return embeddings


def reduce_dimensions(embeddings, dimensions: int = 3):
    """Reduce dimensions of embedded notes to desired dimensions via PCA and return new coordinates

    Input:

    Ouput:
    """
    from sklearn.decomposition import PCA
    pca = PCA(
        n_components=dimensions
    )
    start = time.time()
    projected = pca.fit_transform(
        embeddings
    )
    logger.info(f"Reduced dimensions from {embeddings.shape[1]}D to {projected.shape[1]}D in {round(time.time() - start)}s")

    return projected
