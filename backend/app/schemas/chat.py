from pydantic import BaseModel, field_validator


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str 
    conversation_history: list[ChatMessage] = []
    
    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip(): 
            raise ValueError("Query must not be empty")
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    source_concepts: list[dict]
    context_found: bool