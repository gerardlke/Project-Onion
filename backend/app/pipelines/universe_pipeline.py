from sklearn.decomposition import PCA


async def project_embedding(dimensions: int = 3, embedding):
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

    if not embedding:
        return []

    # Edge case: PCA requires n_components <= n_samples
    actual_dimensions = min(
        dimensions,
        embedding.shape[0]
    )

    pca = PCA(
        n_components=actual_dimensions
    )

    projected = pca.fit_transform(
        embeddings
    )

    return {"coordinates": projected.tolist()}