import numpy as np
from sklearn.decomposition import PCA

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def project_embeddings(embeddings: list[list[float]], dimensions: int = 3):
    """Generates coordinates for all concept embeddings belonging to a user

    Input: 

    Output: {
        "coordinates": [x, y, ...]
    }
    """
    if not embeddings:
        return []
    
    if dimensions < 2:
        raise ValueError(
            "Universe must have at least 2 dimensions"
        )
    
    matrix = np.array(embeddings)
    
    n_samples, n_features = matrix.shape

    if n_samples < dimensions:
        logger.warning(
            f"{n_samples} concept(s) available - cannot project to {dimensions}D."
            f"Falling back to {n_samples}D. More uploads will produce a richer universe."
        )
        dimensions = n_samples

    pca = PCA(n_components=dimensions)
    projected = pca.fit_transform(matrix)

    return projected.tolist()