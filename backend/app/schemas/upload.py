from pydantic import BaseModel


class ConceptFrequency(BaseModel):
    concept: str
    frequency: int

class ConceptPreview(BaseModel):
    chunk_index: int
    concepts: list[ConceptFrequency]

class UploadResponse(BaseModel):
    filename: str
    num_chunks: int
    concepts: list[ConceptPreview]
    status: str