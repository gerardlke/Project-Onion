import numpy as np

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def project_embeddings(embeddings: list[list[float]], dimensions: int = 3):
    """Generates coordinates for all concept embeddings belonging to a user
    using numpy-only PCA — no scikit-learn or scipy dependency.

    Input:
        embeddings:  list of embedding vectors, one per concept
        dimensions:  target dimensionality (2 or 3)

    Output:
        list of coordinate lists, same order as input embeddings
    """
    if not embeddings:
        return []

    if dimensions < 2:
        raise ValueError("Universe must have at least 2 dimensions")

    matrix = np.array(embeddings)   # shape: (n_concepts, n_features)
    n_samples, n_features = matrix.shape

    if n_samples < dimensions:
        logger.warning(
            f"{n_samples} concept(s) available — cannot project to {dimensions}D. "
            f"Falling back to {n_samples}D. More uploads will produce a richer universe."
        )
        dimensions = n_samples

    centred = matrix - matrix.mean(axis=0)

    cov = np.cov(centred.T)

    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx]

    projected = centred @ eigenvectors[:, :dimensions]

    return projected.tolist()