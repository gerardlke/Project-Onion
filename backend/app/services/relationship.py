import os
import time
import asyncio
import requests
from dotenv import load_dotenv
from transformers import pipeline as hf_pipeline

from app.db.operations import (
    get_similar_concepts_by_concept_id,
    create_relation,
    get_all_relation_types
)

### Set up configs and logger
from app.configs.config import (
    SIMILARITY_THRESHOLD,
    RELATIONSHIP_LIMIT,
    CONFIDENCE_THRESHOLD,
    LOCAL_DEPLOYMENT,
    NLI_MODEL
)
from app.logging import setup_logger
logger = setup_logger(__name__)
load_dotenv()

# API NLI model
HF_API_URL = f"https://api-inference.huggingface.co/models/{NLI_MODEL}"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

# Local NLI model
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


async def nli_warm_up():
    """Pre-load the NLI model into memory during application startup before first call"""
    logger.info("Warming up NLI model...")
    await asyncio.to_thread(_get_nli)
    logger.info("NLI model warm-up complete")


def local_classify_relation(source: dict, target: dict, type_lookup: dict):
    """Classify the relationship between two concepts using a local zero-shot NLI model

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
    relation_type = type_lookup.get(top_label)

    logger.info(f"Classified '{source.get("name")}' and '{target.get("name")}' as {relation_type["name"]} ({confidence * 100:.2f}%)")

    return relation_type["id"], confidence


def api_classify_relation(source: dict, target: dict, type_lookup: dict):
    """Classify the relationship between two concepts using an NLI API

    Input:
        source:      concept dict with keys: name, raw_text
        target:      concept dict with keys: name, raw_text
        type_lookup: dict mapping type name

    Output:
        (relation_type dict from DB, confidence float)
    """
    sequence = (
        f"'{source.get('name', '')}': {source.get('raw_text', '')} "
        f"and '{target.get('name', '')}': {target.get('raw_text', '')}"
    )
    payload = {"inputs": sequence, "parameters": {"candidate_labels": list(type_lookup.keys())}}
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)

    result = response.json()
    
    top_label = result["labels"][0]
    confidence = result["scores"][0]
    relation_type = type_lookup.get(top_label)
    
    logger.info(f"Classified '{source.get("name")}' and '{target.get("name")}' as {relation_type["name"]} ({confidence * 100:.2f}%)")

    return relation_type["id"], confidence


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
        r["description"]: r
        for r in relation_types
    }

    failed = []
    start = time.time()
    seen_pairs = set()

    for concept in concepts:
        try:
            # For each concept get their similar concepts
            logger.info(f"Finding similar concepts for '{concept.get("name", "")}'")
            similar_concepts = get_similar_concepts_by_concept_id(
                db=db,
                user_id=user_id,
                concept_id=concept["id"],
                embedding=concept["embedding"],
                threshold=SIMILARITY_THRESHOLD,
                limit=RELATIONSHIP_LIMIT
            )

            # For each similar concept, identify and create the type of relationship
            for neighbour in similar_concepts:

                # Prevent duplicated relationships
                pair = frozenset([concept["id"], neighbour["id"]])
                if pair in seen_pairs:
                    continue
                
                if LOCAL_DEPLOYMENT:
                    relation_type_id, confidence = local_classify_relation(
                        source=concept, 
                        target=neighbour, 
                        type_lookup=type_lookup
                    )
                else:
                    relation_type_id, confidence = api_classify_relation(
                        source=concept, 
                        target=neighbour, 
                        type_lookup=type_lookup
                    )

                if relation_type_id is None or confidence < CONFIDENCE_THRESHOLD:
                    logger.warning(f"No relation type resolved for '{concept.get('name')}' and '{neighbour.get('name')}'. Skipping...")
                    continue
                
                create_relation(
                    db=db,
                    source_id=concept["id"],
                    target_id=neighbour["id"],
                    relation_type_id=relation_type_id,
                    weight=round(1.0-neighbour["distance"], 3),
                    explanation=""
                )

                seen_pairs.add(pair)

            logger.info(f"{len(similar_concepts)} relation edges formed for '{concept.get("name", "")}")

        except Exception as e:
            logger.error(f"Relationship generation failed for concept '{concept.get('name', '')}' (id={concept.get('id')}): {e}")
            failed.append(concept.get("id"))
        
    summary = {
        "concepts_processed": len(concepts),
        "relationships_created": seen_pairs,
        "failed_concept_ids": failed,
        "time_taken": round(time.time() - start)
    }
    logger.info(f"Relationship generation complete: {summary}")
    return summary