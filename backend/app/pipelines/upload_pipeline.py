from fastapi import UploadFile, BackgroundTasks

from app.pipelines.relationship_pipeline import run_relationship_pipeline
from app.services.extract import extract_text
from app.services.chunk import chunk_text
from app.services.concepts import (
    extract_concepts,
    find_existing
)
from app.services.embed import (
    generate_embeddings
)

from app.db.operations import (
    get_topic_by_name,
    create_document,
    create_batch_concept
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def process_document(db, user, file: UploadFile, topic_name: str, background_tasks: BackgroundTasks, **kwargs):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """
    # Extract raw text and save topic/document to db first
    print("extracting text")
    raw_text = await extract_text(file)
    
    topic = get_topic_by_name(db, topic_name)[0]

    print("creating document")
    document = create_document(
        db=db,
        topic_id=topic["id"],
        filename=file.filename,
        content_type=file.content_type,
        raw_text=raw_text
    )

    # Break text up into chunks, then extract concept names and descriptions
    print("chunking document")
    concepts_dict = {}
    chunks = chunk_text(raw_text)
    for chunk in chunks:
        concepts = await extract_concepts(chunk)
        for c in concepts:
            if c.get("name", ""):

                # Aggregate concepts to reduce cluster
                match = find_existing(c.get("name"), concepts_dict)

                if match is not None:
                    concepts_dict[match]["raw_text"] += c.get("description", "")
                else:
                    concepts_dict[c.get("name")] = {
                        "document_id": document.id,
                        "name": c.get("name"),
                        "raw_text": c.get("description", "")
                    }

    # Embed aggregated concepts
    print("embedding document")
    batch_concepts, concepts = [], []
    for name, concept in concepts_dict.items():
        concept["embedding"] = generate_embeddings(concept.get("raw_text", ""))
        batch_concepts.append(concept)
        concepts.append(name)

    print("saving document")
    # Save concepts to db in batches
    create_batch_concept(
        db=db,
        batch_concepts=batch_concepts
    )

    logger.info(f"Batch uploaded content for {len(batch_concepts)} concepts")

    # Start relationship generation pipeline here
    background_tasks.add_task(
        run_relationship_pipeline,
        concept_names=concepts,
        user_id=user["id"]
    )

    logger.info(f"Relationship generation scheduled for {len(concepts)} concept(s)")

    # Return metadata to upload route
    return {
        "id": document.id,
        "num_chunks": len(chunks),
        "concepts": concepts
    }