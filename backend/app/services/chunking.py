# TODO: Move to config file later
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text: str):
    """Chunks text into smaller chunks

    Input:

    Ouput:
    """

    chunks = []
    start = 0

    # TODO: Find a more efficient chunking method
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks