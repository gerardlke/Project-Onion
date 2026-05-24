from fastapi import UploadFile

from app.services.extraction import extract_text
from app.services.chunking import chunk_text
from app.services.concepts import extract_concepts
from app.db.operations import create_document, create_concepts
from app.schemas.upload import PipelineDocument


async def process_document(file: UploadFile, db, **kwargs):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """
    # Extraction pipeline
    raw_text = await extract_text(file)
    chunks = chunk_text(raw_text)
    concepts = extract_concepts(chunks)

    # Build internal object
    pipeline_document = PipelineDocument(
        filename=file.filename,
        content_type=file.content_type,
        raw_text=raw_text,
        chunks=chunks,
        concepts=concepts
    )

    # Save to DB
    document = create_document(
        db=db,
        filename=file.filename,
        raw_text=raw_text
    )
    create_concepts(
        db=db,
        document_id=document.id,
        pipeline_document=pipeline_document
    )

    # Return metadata to upload route
    return {
        "id": document.id,
        "chunks": len(chunks),
        "concepts": len(concepts)
    }