import json
import numpy as np
from sklearn.decomposition import PCA


async def project_embedding(embedding, dimensions: int = 3):
    """Generates coordinates for all concept embeddings belonging to a user

    Input: 

    Output: {
        "coordinates": [x, y, ...]
    }
    """
    if dimensions < 2:
        raise ValueError(
            "Universe must have at least 2 dimensions"
        )
    
    # Convert string to list if needed, then to 2D numpy array 
    if isinstance(embedding, str):
        embedding = json.loads(embedding)
    if not embedding:
        return []
    embedding = np.array(embedding).reshape(1, -1)

    # Ensure n_components is valid based on the entire dataset
    n_samples, n_features = embedding.shape
    n_components = min(dimensions, n_samples, n_features)

    pca = PCA(n_components=n_components)

    print("SHAPE:", embedding.shape)

    projected = pca.fit_transform(embedding)
    print("COORDS:", projected.tolist())
    return projected.tolist()[0]