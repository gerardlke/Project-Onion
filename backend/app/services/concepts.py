import re
import json
from rapidfuzz import fuzz
from openai import AsyncOpenAI
from collections import defaultdict

from app.logging import setup_logger


### Set up configs
from app.configs.config import (
    MINI_LLM, 
    CONCEPT_EXTRACTION_PROMPT
)


### Set up mini LLM
client = AsyncOpenAI()  # reads OPENAI_API_KEY from env


async def extract_concepts(chunk_text: str):
    """Ask LLM to extract meaningful concepts from a single chunk. Returns list of {"name": str, "description": str}

    Input:

    Ouput:
    """
    prompt = CONCEPT_EXTRACTION_PROMPT.format(chunk_text=chunk_text)

    response = await client.chat.completions.create(
        model=MINI_LLM,  # cheap and capable enough for extraction
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # deterministic extraction, not creative generation
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if the model wraps output despite instructions
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
        concepts = parsed.get("concepts", [])
        # Basic validation
        return [
            c for c in concepts
            if isinstance(c.get("name"), str) and isinstance(c.get("description"), str)
        ]
    except json.JSONDecodeError:
        # Don't crash the pipeline — log and return empty
        print(f"[concept_extraction] Failed to parse JSON from chunk: {raw[:200]}")
        return []

def find_existing(name: str, aggregated: dict, threshold: int = 85):
    """
    Return name of best matching concept or None using fuzzy string match on lowercased names

    Input:

    Ouput:
    """
    best_match, best_score = None, 0.0
    for i, existing in enumerate(aggregated):
        fuzzy_ratio = fuzz.ratio(name.lower(), existing["concept"].lower())
        if fuzzy_ratio >= threshold and fuzzy_ratio > best_score:
            best_match = existing["concept"]
            best_score = fuzzy_ratio
    return best_match
