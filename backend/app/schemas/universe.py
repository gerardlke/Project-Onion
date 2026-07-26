from pydantic import BaseModel


class TopicNode(BaseModel):
    id: int
    name: str
    description: str

class TopicResponse(BaseModel):
    nodes: list[TopicNode]

class TopicDetailResponse(BaseModel):
    id: int
    topic: str
    description: str

class ConceptNode(BaseModel):
    id: int
    topic_id: int | None
    coordinates: list[float]
    text_length: int

class NodeResponse(BaseModel):
    nodes: list[ConceptNode]

class NodeDetailResponse(BaseModel):
    id: int
    topic_name: str
    concept: str
    text: str

class RelationEdge(BaseModel):
    id: int
    source_id: int 
    target_id: int
    name: str
    explanation: str
    weight: float

class RelationResponse(BaseModel):
    edges: list[RelationEdge]

class RelationDetailResponse(BaseModel):
    id: int
    name: str
    weight: float
    description: str
    explanation: str