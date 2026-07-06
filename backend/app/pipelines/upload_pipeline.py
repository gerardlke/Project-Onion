from fastapi import UploadFile, BackgroundTasks

from app.pipelines.relationship_pipeline import run_relationship_pipeline
from app.services.extract import extract_text
from app.services.chunk import chunk_text
from app.services.progress import ProgressTracker
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
    update_concept_embedding,
    create_concept_to_document
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def process_document(db, user, file: UploadFile, topic_name: str, background_tasks: BackgroundTasks, tracker: ProgressTracker, **kwargs):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """
    try:
        # Extract text
        await tracker.update("Extracting text from file...", percent=5)
        raw_text = await extract_text(file)

        # Create document in db
        await tracker.update("Saving document record...", percent=10)
        topic = get_topic_by_name(db, topic_name)[0]
        document = create_document(
            db=db,
            topic_id=topic["id"],
            filename=file.filename,
            content_type=file.content_type,
            raw_text=raw_text
        )

        # Chunk text
        await tracker.update("Chunking document into segments...", percent=15)
        chunks = chunk_text(raw_text)

        # Concept extraction
        concepts_dict = {}
        for i, chunk in enumerate(chunks):
            percent = 15 + int((i / len(chunks)) * 50)  # Progress moves from 15% to 65% across all chunks
            await tracker.update(
                f"Extracting concepts from segment {i + 1} of {len(chunks)}...",
                percent=percent
            )

            concepts = await extract_concepts(chunk)
            for c in concepts:
                if not c.get("name"):
                    continue
                name = c.get("name")
                description = c.get("description", "")
                match = find_existing(name, concepts_dict, description=description)
                if match is not None:
                    concepts_dict[match]["raw_text"] += ". " + description
                else:
                    concepts_dict[name] = {
                        "user_id": user["id"],
                        "name": name,
                        "raw_text": description
                    }

        await tracker.update(
            f"Found {len(concepts_dict)} unique concept(s).", percent=65
        )

        # Embedding concepts
        await tracker.update("Generating semantic embeddings...", percent=70)
        batch_concepts = []
        for concept in concepts_dict.values():
            concept["embedding"] = generate_embeddings(concept.get("raw_text", ""))
            batch_concepts.append(concept)

        # Saving to db
        await tracker.update("Saving concepts to database...", percent=80)
        all_concepts = create_batch_concept(db=db, batch_concepts=batch_concepts)
        updated  = [c for c in all_concepts if c["updated"]]

        # Re-embedding for updated concepts 
        if updated:
            await tracker.update(
                f"Re-embedding {len(updated)} merged concept(s)...", percent=85
            )
            for concept in updated:
                new_embedding = generate_embeddings(concept.get("raw_text", ""))
                update_concept_embedding(db, concept["id"], new_embedding)
                concept["embedding"] = new_embedding

        # Adding junction table relation to db
        await tracker.update("Recording document provenance...", percent=90)
        for concept in all_concepts:
            create_concept_to_document(
                db=db,
                concept_id=concept["id"],
                document_id=document["id"]
            )

        # Starting relationship generation for all new/updated concepts
        await tracker.update("Scheduling relationship generation...", percent=95)
        concept_names = [c["name"] for c in all_concepts]
        background_tasks.add_task(
            run_relationship_pipeline,
            concept_names=concept_names,
            user_id=user["id"]
        )

        await tracker.complete(
            message=(
                f"Upload complete — {len(inserted)} new concept(s), "
                f"{len(updated)} merged. "
                f"Relationships generating in background."
            ),
            metadata={
                "document_id": document.id,
                "num_chunks": len(chunks),
                "new_concepts": len(inserted),
                "merged_concepts": len(updated),
            }
        )

    except Exception as e:
        logger.exception(f"Upload pipeline failed for '{file.filename}': {e}")
        await tracker.error(f"Upload failed: {str(e)}")
        raise