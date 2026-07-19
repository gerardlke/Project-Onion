import os
import time
import asyncio
import numpy as np
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


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
_hf_client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN"),
)

# Local encoder
_encoder = None

def _get_encoder():
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
    _get_encoder()
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
    embeddings = []
    for text in concepts:
        result = _hf_client.feature_extraction(
            text,
            model=ENCODER,
        )
        arr = np.array(result)
        
        if arr.ndim == 2:
            arr = arr.mean(axis=0)
        embeddings.append(arr.tolist())
    return embeddings


async def generate_embeddings(concepts: list[str]):
    """Embeds concepts using preset encoder 

    Input:

    Ouput:
    """
    start = time.time()

    if LOCAL_DEPLOYMENT:
        embeddings = await asyncio.to_thread(local_embed, concepts)
    else:
        try:
            embeddings = await asyncio.to_thread(api_embed, concepts)
        except Exception as e:
            logger.warning(f"HF InferenceClient failed ({e}) — falling back to local encoder")
            embeddings = await asyncio.to_thread(local_embed, concepts)

    logger.info(
        f"Embeddings generated for {len(concepts)} concept(s) "
        f"in {round(time.time() - start, 2)}s"
    )
    return embeddings
