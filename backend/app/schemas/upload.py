from pydantic import BaseModel


class NewTopicResponse(BaseModel):
    success: bool
    name: str
    description: str

class TopicResponse(BaseModel):
    name: str
    description: str

class GetTopicResponse(BaseModel):
    success: bool
    topics: list[TopicResponse]

class UploadResponse(BaseModel):
    success: bool
    topic: str
    filename: str
    content_type: str
    size_mb: float
    document_id: int
    num_chunks: int
    concepts: str

class RawConcept(BaseModel):
    name: str
    text: str