from pydantic import BaseModel


class UniverseNode(BaseModel):
    id: int
    concept: str
    frequency: int
    x: float
    y: float
    z: float | None

class UniverseResponse(BaseModel):
    nodes: list[UniverseNode]

class NodeDetailResponse(BaseModel):
    id: int
    concept: str
    frequency: int
    chunk_index: int
    document_id: int
    x: float
    y: float
    z: float | None