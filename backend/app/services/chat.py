### Set up configs
from app.configs.config import RAG_SYSTEM_PROMPT

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


def build_context_block(retrieved_concepts: list[dict]):
    """Format retrieved concepts into a readable context block for the prompt.

    Input: Each concept is presented as its name and source text so LLM has both label and the explanation as context

    Output:
    """
    if not retrieved_concepts:
        return "No relevant concepts were found in the student's uploaded notes."
    
    blocks = []
    for concept in retrieved_concepts:
        blocks.append(
            f"Concept: {concept['name']}\n"
            f"Notes: {concept['raw_text']}"
        )
    return "\n---\n".join(blocks)


def build_prompt(query: str, retrieved_concepts: list[dict], conversation_history: list[dict]):
    """Build the full message list for the LLM

    Input:
        query:                The user's current question
        retrieved_concepts:   Concepts retrieved from pgvector search
        conversation_history: Prior turns as [{role, content}] from frontend

    Output: Full message list ready to pass to generate()
    """
    context_block = build_context_block(retrieved_concepts)
    system_content = RAG_SYSTEM_PROMPT.strip().format(context=context_block)

    print("SYSTEM CONTENT", system_content)

    messages = [{"role": "system", "content": system_content}]

    # Include prior conversation turns for multi-turn coherence
    messages.extend(conversation_history)

    # Append the current query as the final user turn
    messages.append({"role": "user", "content": query})

    return messages