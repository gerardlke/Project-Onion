from fastapi import UploadFile

from app.services.extraction import extract_text
from app.services.chunking import chunk_text
from app.services.concepts import extract_concepts


async def process_document(file: UploadFile, **kwargs):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """
    raw_text = await extract_text(file)
    chunks = chunk_text(raw_text)
    concepts = extract_concepts(chunks)

    # TODO: Save to DB later
    # save_document_data(
    #     raw_text,
    #     chunks,
    #     concepts
    # )

    return {
        "raw": raw_text,
        "chunks": chunks,
        "concepts": concepts
    }