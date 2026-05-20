from app.services.ingestion import extract_text
from app.services.chunking import chunk_text
from app.services.extraction import extract_concepts

def process_document(file_path):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """

    raw_text = extract_text(file_path)
    chunks = chunk_text(raw_text)
    concepts = extract_concepts(chunks)

    # TODO: Save to DB later
    # save_document_data(
    #     raw_text,
    #     chunks,
    #     concepts
    # )

    return {
        "chunks": chunks,
        "concepts": concepts
    }