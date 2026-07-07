import time
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

### Set up configs
from app.configs.config import (
    ENCODER
)

### Set up logger for model logs
from app.logging import setup_logger
logger = setup_logger(__name__)

_encoder = None

async def _get_encoder():
    """Lazily load encoder on first call, then reuse"""
    global _encoder
    if _encoder is not None:
        return _encoder
    
    logger.info("Setting up encoder")
    _encoder = SentenceTransformer(ENCODER)
    logger.info("Encoder downloaded")

    return _encoder


async def encoder_warm_up():
    """Pre-load the encoder into memory during application startup before first call"""
    logger.info("Warming up encoder...")
    await _get_encoder()
    logger.info("Encoder warm-up complete")


async def generate_embeddings(concepts: list[str]):
    """Embeds concepts using loaded encoder 

    Input:

    Ouput:
    """
    model = await _get_encoder()
    start = time.time()
    embeddings = model.encode(
        concepts,
        convert_to_numpy=True
    )
    logger.info(f"Embeddings generated for {len(concepts)} concept(s) in {round(time.time() - start)}s")
    return embeddings.tolist()


def reduce_dimensions(embeddings, dimensions: int = 3):
    """Reduce dimensions of embedded notes to desired dimensions via PCA and return new coordinates

    Input:

    Ouput:
    """
    pca = PCA(
        n_components=dimensions
    )
    start = time.time()
    projected = pca.fit_transform(
        embeddings
    )
    logger.info(f"Reduced dimensions from {embeddings.shape[1]}D to {projected.shape[1]}D in {round(time.time() - start)}s")

    return projected
