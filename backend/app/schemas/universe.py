from typing import Optional
from pydantic import BaseModel


class TopicResponse(BaseModel):


class UniverseNode(BaseModel):
    id: int
    concept: str
    frequency: int
    x: float
    y: float
    z: float | None

class NodeResponse(BaseModel):
    nodes: list[UniverseNode]

class NodeDetailResponse(BaseModel):
    id: int
    concept: str
    frequency: int
    chunk_index: Optional[int] = None
    document_id: int
    x: float
    y: float
    z: float | None

class RelationResponse(BaseModel):
    