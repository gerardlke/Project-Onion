import re
import json
from rapidfuzz import fuzz

from app.services.llm import generate

### Set up configs
from app.configs.config import CONCEPT_EXTRACTION_PROMPT

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

    # Strip markdown fences — small local models do this even more often
    # than hosted models, since they're less reliably instruction-following
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

def find_existing(name: str, aggregated: dict, threshold: int = 85):
    """
    Return name of best matching concept or None using fuzzy string match on lowercased names

    Input:

    Ouput:
    """
    best_match, best_score = None, 0.0
    for existing in aggregated:
        fuzzy_ratio = fuzz.ratio(name.lower(), aggregated[existing]["name"].lower())
        if fuzzy_ratio >= threshold and fuzzy_ratio > best_score:
            best_match = aggregated[existing]["name"]
            best_score = fuzzy_ratio
    return best_match
