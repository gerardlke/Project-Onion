from fastapi import UploadFile

from app.services.extract import extract_text
from app.services.chunk import chunk_text
from app.services.concepts import extract_concepts
from app.services.embed import generate_embeddings, reduce_dimensions

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

    # Embedding and reducing to get latent positions in universe
    concept_strings = [concept.concept for concept in concepts]
    embeddings = generate_embeddings(
        concept_strings
    )
    coordinates = reduce_dimensions(
        embeddings,
        dimensions=3
    )
    for concept, coordinate in zip(concepts, coordinates):
        concept.x = float(coordinate[0])
        concept.y = float(coordinate[1])
        concept.z = float(coordinate[2])

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