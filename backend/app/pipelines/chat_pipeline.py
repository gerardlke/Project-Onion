import re
import json

from app.services.embed import generate_embeddings
from app.services.chat import build_prompt
from app.services.llm import generate
from app.db.operations import search_concepts_by_embedding

### Set up configs
from app.configs.config import (
    RAG_TOP_K,
    RAG_DISTANCE_THRESHOLD
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


async def process_chat_query(db, user_id: int, query: str, conversation_history: list[dict]):
    """RAG pipeline for a single chat turn.

    Input:
        db:                   SQLAlchemy session
        user_id:              scopes retrieval to this user's concepts
        query:                user's current message
        conversation_history: prior [{role, content}] turns from frontend

    Output:
        {
            "response":         str of LLM's answer
            "source_concepts":  list of dict{id, name} of concepts used as context
            "context_found":    bool if relevant concepts were retrieved
        }
    """
    logger.info(f"RAG query for user {user_id}: '{query[:80]}...'")

    # Embed query
    query_embedding = await generate_embeddings([query])
    query_embedding = query_embedding[0]

    # Retrieve nearest concepts for context
    retrieved_concepts = search_concepts_by_embedding(
        db=db,
        user_id=user_id,
        query_embedding=query_embedding,
        limit=RAG_TOP_K,
        distance_threshold=RAG_DISTANCE_THRESHOLD
    )

    context_found = len(retrieved_concepts) > 0

    if not context_found:
        logger.info(f"No relevant concepts found for query: '{query[:60]}...'")

    # Build prompt
    messages = build_prompt(
        query=query,
        retrieved_concepts=retrieved_concepts,
        conversation_history=conversation_history
    )

    # Generate response
    raw = await generate(
        messages=messages,      
        max_new_tokens=700,
        temperature=0.3  # slight temperature for natural conversation
    )

    # Strip markdown fences if model wraps output
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
        response = parsed.get("response", raw)
        citations = parsed.get("citations", [])
        knowledge_gaps = parsed.get("knowledge_gaps", [])
    except (json.JSONDecodeError, KeyError):
        logger.warning("Chat response was not valid JSON - returning raw text")
        response = raw
        citations = knowledge_gaps = []

    logger.info(f"RAG response generated for user {user_id}")

    return {
        "response": response,
        "citations":      citations,        # [{concept, quote}]
        "knowledge_gaps": knowledge_gaps,   # [concept name strings]
        "source_concepts": [
            {"id": c["id"], "name": c["name"]}
            for c in retrieved_concepts
        ],
        "context_found": context_found
    }