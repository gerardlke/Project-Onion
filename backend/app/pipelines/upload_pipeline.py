from fastapi import UploadFile

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


async def process_document(db, user, file: UploadFile, topic_name: str, **kwargs):
    """Main pipeline orchestration for upload process

    Input:

    Ouput:
    """
    # Extract raw text and save topic/document to db first
    raw_text = await extract_text(file)
    
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

    # Save concepts to db in batches
    create_batch_concept(
        db=db,
        batch_concepts=batch_concepts
    )

    # TODO: Start relationship generation pipeline here

    # Return metadata to upload route
    return {
        "id": document.id,
        "num_chunks": len(chunks),
        "concepts": concepts
    }