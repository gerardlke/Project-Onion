# Upload configs
SUPPORTED_EXTENSIONS={".txt", ".md", ".docx", ".pdf", ".pptx"}
MAX_FILE_SIZE_MB=50

# Model configs
LOCAL_DEPLOYMENT = False
ENCODER = "all-MiniLM-L6-v2"
LOCAL_LLM = "Qwen/Qwen2.5-1.5B-Instruct"
API_LLM = "llama-3.1-8b-instant"
LOCAL_NLI = "cross-encoder/nli-deberta-v3-small"

# Concept aggregation configs
FUZZY_ACCEPT_THRESHOLD = 90
FUZZY_REJECT_THRESHOLD = 50
EMBEDDING_SIMILARITY_THRESHOLD = 0.80

# Relationship configs
SIMILARITY_THRESHOLD = 0.7
RELATIONSHIP_LIMIT = 10
CONFIDENCE_THRESHOLD = 0.5

# Database configs
RESET_DB = False

# Concept extraction configs
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
CONCEPT_EXTRACTION_PROMPT = """
    You are extracting key concepts from a student's study notes.\n
    A concept is a meaningful idea, process, algorithm, principle, or mechanism — NOT a simple noun or entity name.\n
    Good concepts: "AVL Rotation", "Inorder Traversal", "Amortized Time Complexity"
    Bad concepts: "Tree", "Node", "Algorithm"\n
    For each concept, return:
    - name: a short, specific phrase (2-5 words)
    - description: one sentence explaining the core idea\n
    Return JSON only. No explanation outside the JSON.\n
    Format:
    {{
        "concepts": [
            {{"name": "...", "description": "..."}},
            ...
        ]
    }}

    Text:
    \"\"\"
    {chunk_text}
    \"\"\"
"""

# RAG chatbot configs
RAG_TOP_K = 10
RAG_DISTANCE_THRESHOLD = 0.6
RAG_SYSTEM_PROMPT = """You are a study assistant helping a student understand concepts from their own uploaded notes.

    You have been provided with relevant excerpts from the student's notes as context.
    Answer the student's question using ONLY the provided context.
    If the context does not contain enough information to answer the question, say so clearly — do not invent information.
    Keep answers concise and educational. Reference specific concepts from the context by name where relevant.

    Context from student's notes:
    {context}
"""