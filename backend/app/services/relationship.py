import os
import time
import asyncio
import json
import re
from dotenv import load_dotenv

from app.db.operations import (
    get_similar_concepts_by_concept_id,
    create_relation,
    get_all_relation_types
)
from app.services.llm import generate

### Set up configs and logger
from app.configs.config import (
    SIMILARITY_THRESHOLD,
    RELATIONSHIP_LIMIT,
    CONFIDENCE_THRESHOLD,
    RELATION_CLASSIFICATION_PROMPT
)
from app.logging import setup_logger
logger = setup_logger(__name__)
load_dotenv()


async def classify_relation(source: dict, target: dict, type_lookup: dict) -> tuple:
    """Classify relationship between two concepts using the LLM

    Input:
        source:      concept dict with keys: name, raw_text
        target:      concept dict with keys: name, raw_text
        type_lookup: dict mapping relation description → DB relation type row

    Output:
        (relation_type_id, confidence, explanation)
    """
    prompt = RELATION_CLASSIFICATION_PROMPT.strip().format(
        source_name=source.get("name", ""),
        source_text=source.get("raw_text", "")[:300],
        target_name=target.get("name", ""),
        target_text=target.get("raw_text", "")[:300],
    )

    try:
        raw = await generate(prompt=prompt, max_new_tokens=200, temperature=0.0)

        # Strip markdown fences if model wraps output despite instructions
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)
        relationship = parsed.get("relationship", "").upper()
        confidence   = float(parsed.get("confidence", 0.0))
        explanation  = parsed.get("explanation", "")

        # Match returned type name to a DB relation type row
        matched_type = next(
            (r for r in type_lookup.values() if r["name"] == relationship), None
        )

        if matched_type is None:
            logger.warning(
                f"LLM returned unknown relationship type '{relationship}' "
                f"for '{source.get('name')}' → '{target.get('name')}'. "
                f"Falling back to SIMILAR."
            )
            matched_type = next(
                (r for r in type_lookup.values() if r["name"] == "SIMILAR"), None
            )

        logger.info(f"Classified '{source.get('name')}' and '{target.get('name')}' as {matched_type['name'] if matched_type else 'UNKNOWN'} ({confidence * 100:.1f}%): {explanation}")
        return matched_type["id"] if matched_type else None, confidence, explanation

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning(
            f"LLM classification parse failed for "
            f"'{source.get('name')}' → '{target.get('name')}': {e}. "
            f"Falling back to SIMILAR."
        )
        fallback = next(
            (r for r in type_lookup.values() if r["name"] == "SIMILAR"), None
        )
        return (fallback["id"] if fallback else None), 0.0, ""


async def generate_relationships(db, concepts: list, user_id: int):
    """Generate relationships for all concepts from a single upload batch

    Input:
        db:       SQLAlchemy session (pipeline-owned)
        concepts: list of concept dicts — id, name, raw_text, embedding
        user_id:  scopes similarity search to this user's universe

    Output:
        Summary dict with counts and timing
    """
    relation_types = get_all_relation_types(db=db)
    if not relation_types:
        logger.error("No relation types in DB — ensure seed data is loaded")
        return {"concepts_processed": 0, "relationships_created": 0, "failed_concept_ids": []}

    type_lookup = {r["description"]: r for r in relation_types}

    failed = []
    start = time.time()
    seen_pairs: set[frozenset] = set()

    for concept in concepts:
        try:
            logger.info(f"Finding similar concepts for '{concept.get('name', '')}'")

            similar_concepts = get_similar_concepts_by_concept_id(
                db=db,
                user_id=user_id,
                concept_id=concept["id"],
                embedding=concept["embedding"],
                threshold=SIMILARITY_THRESHOLD,
                limit=RELATIONSHIP_LIMIT
            )

            for neighbour in similar_concepts:
                pair = frozenset([concept["id"], neighbour["id"]])
                if pair in seen_pairs:
                    continue

                relation_type_id, confidence, explanation = await classify_relation(
                    source=concept,
                    target=neighbour,
                    type_lookup=type_lookup
                )

                if relation_type_id is None or confidence < CONFIDENCE_THRESHOLD:
                    logger.warning(
                        f"Skipping low-confidence pair: "
                        f"'{concept.get('name')}' → '{neighbour.get('name')}' "
                        f"({confidence:.2f})"
                    )
                    continue

                create_relation(
                    db=db,
                    source_id=concept["id"],
                    target_id=neighbour["id"],
                    relation_type_id=relation_type_id,
                    weight=round(1.0 - neighbour["distance"], 3),
                    explanation=explanation   # CHANGED: now populated from LLM
                )
                seen_pairs.add(pair)

            logger.info(f"{len(similar_concepts)} relation edge(s) processed for '{concept.get('name', '')}'")

        except Exception as e:
            logger.error(f"Relationship generation failed for '{concept.get('name', '')}' (id={concept.get('id')}): {e}")
            failed.append(concept.get("id"))

    summary = {
        "concepts_processed": len(concepts),
        "relationships_created": len(seen_pairs),
        "failed_concept_ids": failed,
        "time_taken": round(time.time() - start)
    }
    logger.info(f"Relationship generation complete: {summary}")
    return summary