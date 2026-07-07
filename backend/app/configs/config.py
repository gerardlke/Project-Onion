# Upload configs
ALLOWED_FILE_TYPES=[".txt", ".docx"]
MAX_FILE_SIZE_MB=500

# Model configs
LOCAL_DEPLOYMENT = True
ENCODER = "all-MiniLM-L6-v2"
MINI_LLM = "gpt-4o-mini"
NLI_MODEL = "cross-encoder/nli-deberta-v3-small"

# Relationship configs
SIMILARITY_THRESHOLD = 0.7
RELATIONSHIP_LIMIT = 10

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