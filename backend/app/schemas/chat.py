from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    conversation_history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    source_concepts: list[dict]
    context_found: bool