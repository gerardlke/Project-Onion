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
    create_batch_concept,
    update_concept_embedding
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def process_document(db, user, file: UploadFile, topic_name: str, background_tasks: BackgroundTasks, **kwargs):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """
    # Extract raw text
    raw_text = await extract_text(file)
    
    # Save current document's topic and document to db first
    topic = get_topic_by_name(db, topic_name)[0]
    document = create_document(
        db=db,
        topic_id=topic["id"],
        filename=file.filename,
        content_type=file.content_type,
        raw_text=raw_text
    )

    # Break text up into chunks, then extract concept names and descriptions
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
    batch_concepts, concepts = [], []
    for name, concept in concepts_dict.items():
        concept["embedding"] = generate_embeddings(concept.get("raw_text", ""))
        batch_concepts.append(concept)
        concepts.append(name)

    # Save concepts to db as a batch
    all_concepts = create_batch_concept(
        db=db,
        batch_concepts=batch_concepts
    )

    # Re-embed updated concepts and update new embeddings in db
    updated_concepts = [concept for concept in all_concepts if concept["updated"]]
    for concept in updated_concepts:
        update_concept_embedding(
            db, 
            concept["id"],
            generate_embeddings(concept.get("raw_text", ""))
        )

    logger.info(f"Batch uploaded content for {len(all_concepts) - len(updated_concepts)} concepts")
    logger.info(f"Updated content for {len(updated_concepts)} concepts")    

    # Start relationship generation pipeline for new concepts
    new_concepts = [concept["name"] for concept in all_concepts if not concept["updated"]]
    background_tasks.add_task(
        run_relationship_pipeline,
        concept_names=new_concepts,
        user_id=user["id"]
    )

    logger.info(f"Relationship generation scheduled for {len(new_concepts)} new concept(s)")

    # Return metadata to upload route
    return {
        "id": document.id,
        "num_chunks": len(chunks),
        "concepts": concepts
    }