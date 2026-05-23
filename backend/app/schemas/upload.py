from pydantic import BaseModel


class ConceptFrequency(BaseModel):
    concept: str
    frequency: int

class ConceptPreview(BaseModel):
    chunk_index: int
    concepts: list[ConceptFrequency]

class UploadResponse(BaseModel):
    success: bool
    filename: str
    content_type: str
    size_mb: float
    concepts: list[ConceptPreview]