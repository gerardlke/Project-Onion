from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA


# TODO: Move to config later
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embeddings(concepts: list[str]):
    """Embeds concepts using encoder 

    Input:

    Ouput:
    """
    embeddings = model.encode(
        concepts,
        convert_to_numpy=True
    )
    return embeddings

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

    return projected