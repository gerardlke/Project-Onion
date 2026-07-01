# Upload configs
ALLOWED_FILE_TYPES=[".txt", ".docx"]
MAX_FILE_SIZE_MB=500

# Model configs
ENCODER = "all-MiniLM-L6-v2"
LLM = "Qwen/Qwen2.5-1.5B-Instruct"

# Concept aggregation configs
FUZZY_ACCEPT_THRESHOLD = 90
FUZZY_REJECT_THRESHOLD = 50
EMBEDDING_SIMILARITY_THRESHOLD = 0.80

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