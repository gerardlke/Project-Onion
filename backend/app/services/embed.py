from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

from app.logging import setup_logger

from app.configs.config import ENCODER


### Set up logger for model logs
logger = setup_logger(__name__)

### Set up configs for encoder
logger.info("Setting up encoder.")
model = SentenceTransformer(ENCODER)
logger.info("Encoder downloaded.")


def generate_embeddings(concepts: list[str]):
    """Embeds concepts using encoder 

    Input:

    Ouput:
    """
    embeddings = model.encode(
        concepts,
        convert_to_numpy=True
    )
    return embeddings.tolist()

def reduce_dimensions(embeddings, dimensions: int = 3):
    """Reduce dimensions of embedded notes to desired dimensions via PCA and return new coordinates

    Input:

    Ouput:
    """
    pca = PCA(
        n_components=dimensions
    )
    projected = pca.fit_transform(
        embeddings
    )
    logger.info(f"Reduced dimensions from {embeddings.shape[1]}D to {projected.shape[1]}D")

    return projected