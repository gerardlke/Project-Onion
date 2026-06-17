from langchain_text_splitters import RecursiveCharacterTextSplitter

### Set up configs
from app.configs.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def chunk_text(text: str):
    """
    Split document into overlapping semantic chunks

    Input:

    Ouput:
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "],
    )
    return splitter.split_text(text)
