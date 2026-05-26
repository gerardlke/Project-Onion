from typing import Optional
from pydantic import BaseModel


class ExtractedConcept(BaseModel):
    concept: str
    frequency: int
    chunk_index: Optional[int] = None
    x: float | None = None
    y: float | None = None
    z: float | None = None

class PipelineDocument(BaseModel):
    filename: str
    content_type: str
    raw_text: str
    chunks: list[str]
    concepts: list[ExtractedConcept]


class UploadResponse(BaseModel):
    success: bool
    filename: str
    content_type: str
    size_mb: float
    document_id: int
    num_chunks: int
    num_concepts: int