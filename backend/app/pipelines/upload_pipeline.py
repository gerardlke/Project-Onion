from fastapi import UploadFile

from app.services.extract import extract_text
from app.services.chunk import chunk_text
from app.services.concepts import extract_concepts
from app.services.embed import generate_embeddings, reduce_dimensions

from app.db.operations import (
    get_topic_by_name,
    create_document,
    create_batch_concept
)
from app.schemas.upload import PipelineDocument


async def process_document(db, user, file: UploadFile, topic_name: str, **kwargs):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """
    # Extract raw text and save topic/document to db first
    raw_text = await extract_text(file)
    
    topic = get_topic_by_name(topic_name)

    document = create_document(
        db=db,
        user_id=user.id,
        topic_id=topic.id
        filename=file.filename,
        raw_text=raw_text
    )

    # Chunk and embed raw text
    chunks = chunk_text(raw_text)
    concepts = extract_concepts(chunks)
    embeddings = generate_embeddings(
        [concept.concept for concept in concepts]
    )

    # Save concepts to db in batches
    concepts = create_batch_concept(
        db=db,
        document_id=document.id,
        concepts=concepts,
        embeddings=embeddings
    )

    # Return metadata to upload route
    return {
        "id": document.id,
        "chunks": len(chunks),
        "concepts": concepts
    }