from transformers import pipeline as hf_pipeline

from app.db.operations import (
    get_similar_concepts,
    create_relation,
    get_all_relation_types,
    get_relation_type_by_name
)

### Set up configs and logger
from app.configs.config import (
    SIMILARITY_THRESHOLD,
    RELATIONSHIP_LIMIT,
    NLI_MODEL
)
from app.logging import setup_logger
logger = setup_logger(__name__)


# Lazy singleton instead of loading at module import time and defers cost to first actual use
_nli = None

def _get_nli():
    """Load NLI classifier on first call and reuse"""
    global _nli
    if _nli is None:
        logger.info("Loading NLI classifier - first call only")
        _nli = hf_pipeline(
            "zero-shot-classification",
            model=NLI_MODEL
        )
        logger.info("NLI classifier loaded")
    return _nli


def classify_relation(source: dict, target: dict, type_lookup: dict):
    """Classify the relationship between two concepts using zero-shot NLI.

    Input:
        source:      concept dict with keys: name, raw_text
        target:      concept dict with keys: name, raw_text
        type_lookup: dict mapping type name

    Output:
        (relation_type dict from DB, confidence float)
    """
    nli = _get_nli()

    sequence = (
        f"'{source.get('name', '')}': {source.get('raw_text', '')} "
        f"and '{target.get('name', '')}': {target.get('raw_text', '')}"
    )

    result = nli(
        sequence,
        list(type_lookup.keys()),
        multi_label=False
    )

    top_label = result["labels"][0]
    confidence = result["scores"][0]

    matched_type = type_lookup.get(top_label)

    logger.info(f"Classified '{source.get("name")}' and '{target.get("name")}' as {matched_type} ({confidence * 100:.2f}%)")

    return matched_type, confidence


def generate_relationships(db, concepts: list, user_id: int):
    """Helper funciton to generate relationships for each uploaded concept

    Input:

    Ouput:
    """
    # Get all relationship types for matching later
    relation_types = get_all_relation_types(db=db)
    if not relation_types:
        logger.error(
            "No relation types found in DB - ensure seed data is loaded"
        )
        return {"concepts_processed": 0, "relationships_created": 0, "failed_concept_ids": []}

    type_lookup = {
        r["description"]: r["name"]
        for r in relation_types
    }

    total = 0
    failed = []

    for concept in concepts:
        try:
            # For each concept get their similar concepts
            logger.info(f"Finding similar concepts for '{concept.get("name", "")}'")
            similar_concepts = get_similar_concepts(
                db=db,
                user_id=user_id,
                concept_id=concept["id"],
                embedding=concept["embedding"],
                threshold=SIMILARITY_THRESHOLD,
                limit=RELATIONSHIP_LIMIT
            )

            # For each similar concept, identify and create the type of relationship
            for neighbour in similar_concepts:
                relation_type_name, confidence = classify_relation(
                    source=concept, 
                    target=neighbour, 
                    type_lookup=type_lookup
                )

                if relation_type_name is None or confidence < 0.5:
                    logger.warning(f"No relation type resolved for '{concept.get('name')}' and '{neighbour.get('name')}' - skipping...")
                    continue

                relation_type = get_relation_type_by_name(db, relation_type_name)[0]
                
                create_relation(
                    db=db,
                    source_id=concept["id"],
                    target_id=neighbour["id"],
                    relation_type_id=relation_type["id"],
                    weight=round(1.0-neighbour["distance"], 3),
                    explanation=""
                )

            total += len(similar_concepts)
            logger.info(f"{len(similar_concepts)} relation edges formed for '{concept.get("name", "")}")

        except Exception as e:
            logger.error(f"Relationship generation failed for concept '{concept.get('name', '')}' (id={concept.get('id')}): {e}")
            failed.append(concept.get("id"))
        
    summary = {
        "concepts_processed": len(concepts),
        "relationships_created": total,
        "failed_concept_ids": failed
    }
    logger.info(f"Relationship generation complete: {summary}")
    return summary