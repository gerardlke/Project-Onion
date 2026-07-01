import re
import json
from rapidfuzz import fuzz
from sklearn.metrics.pairwise import cosine_similarity

from app.services.llm import generate
from app.services.embed import generate_embeddings

### Set up configs
from app.configs.config import (
    CONCEPT_EXTRACTION_PROMPT,
    FUZZY_ACCEPT_THRESHOLD,
    FUZZY_REJECT_THRESHOLD,
    EMBEDDING_SIMILARITY_THRESHOLD
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def extract_concepts(chunk: str):
    """Ask LLM to extract meaningful concepts from a single chunk. Returns list of {"name": str, "description": str}

    Input:

    Output:
    """
    prompt = CONCEPT_EXTRACTION_PROMPT.format(chunk_text=chunk)

    raw = await generate(prompt, max_new_tokens=1000, temperature=0.0)

    # Strip markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
        concepts = parsed.get("concepts", [])
        return [
            c for c in concepts
            if isinstance(c.get("name"), str) and isinstance(c.get("description"), str)
        ]
    except json.JSONDecodeError:
        logger.warning(f"[concept_extraction] Failed to parse JSON from chunk: {raw[:200]}")
        return []

def find_existing(name: str, aggregated: dict):
    """
    Return the key of the best matching concept in aggregated, or None.
    Uses a two-stage approach: Fuzzy string match as a cheap pre-filter, then embedding similarity on 'name: description' for ambiguous pairs

    Input:
        - name:         incoming concept name to match
        - aggregated:   dict of existing concepts keyed by name
        - description:  incoming concept description (improves embedding accuracy)
        - threshold:    unused legacy param — kept for backwards compatibility

    Output:
        Name of matching concept in aggregated, or None
    """
    best_match, best_score = None, 0.0
    possible_matches = []

    # Attempt fuzzy matching first
    for existing_name in aggregated:
        fuzzy_score = fuzz.ratio(name.lower(), existing_name.lower())

        if fuzzy_score >= FUZZY_ACCEPT_THRESHOLD and fuzzy_score > best_score:
            best_match = existing_name
            best_score = fuzzy_score
            continue
        
        if fuzzy_score >= FUZZY_REJECT_THRESHOLD:
            possible_matches.append(existing_name)

    # If a good match above fuzzy threshold has been found already
    if best_match: 
        return best_match

    # If no best match and all get fuzzy rejected, then no possibilities
    if not possible_matches:
        return None

    embedded_matches = generate_embeddings([name] + possible_matches)
    embedded_name = embedded_matches.pop(0)

    # Attempt semantic matching
    for idx, match in enumerate(embedded_matches):
        similarity = cosine_similarity(embedded_name, match)

        if similarity >= EMBEDDING_SIMILARITY_THRESHOLD and similarity > best_score:
            best_match = possible_matches[idx]
            best_score = similarity

    return best_match
