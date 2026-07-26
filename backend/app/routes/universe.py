import json
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.logging import setup_logger
from app.pipelines.authentication_pipeline import get_current_user
from app.pipelines.universe_pipeline import project_embeddings
from app.db.session import get_db
from app.db.operations import (
    get_all_topics_by_user_id,
    get_topic_by_document_id,
    get_topic_by_id,
    get_all_concepts_by_user_id,
    get_concept_by_id,
    get_all_relations_by_user_id,
    get_relation_by_id
)
from app.schemas.user import UserResponse as User
from app.schemas.universe import (
    TopicNode,
    TopicResponse,
    TopicDetailResponse,
    ConceptNode,
    NodeResponse,
    NodeDetailResponse,
    RelationEdge,
    RelationResponse,
    RelationDetailResponse
)


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()


@router.get("/topics", response_model=TopicResponse)
async def get_universe_topics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for extracting all topics from backend to populate universe

    Input:

    Ouput:
    """
    try:
        logger.info(f"Extracting all topics for user '{user["username"]}'")

        # Extract all topics from db then format into TopicNodes
        all_topics = [
            TopicNode(
                id=topic["id"],
                name=topic["name"],
                description=topic["description"],
            ) for topic in get_all_topics_by_user_id(db, user["id"])
        ]

        logger.info(f"Extracted {len(all_topics)} topic nodes")

        return TopicResponse(
            nodes=all_topics
        )

    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting topics for universe: {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    

@router.get("/topic/{topic_id}", response_model=TopicDetailResponse)
async def get_topic_detail(
    topic_id: int,
    db: Session = Depends(get_db)
):
    """API Route for extracting specific topic node data from backend

    Input:

    Ouput:
    """
    try:
        topic = get_topic_by_id(db, topic_id)

        if not topic:
            raise HTTPException(
                status_code=404,
                detail="Topic not found"
            )
        
        topic = topic[0]

        return TopicDetailResponse(
            id=topic["id"],
            topic=topic["name"],
            description=topic["description"]
        )
    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting topic internal data due to {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/nodes", response_model=NodeResponse)
async def get_universe_nodes(
    dimensions: int = 3,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for extracting all concept nodes from backend to populate universe

    Input:

    Ouput:
    """
    try:
        logger.info(f"Extracting concept nodes for user '{user["username"]}'")

        # Extract all concepts from db, project all coordinates, then format into ConceptNodes
        concepts = get_all_concepts_by_user_id(db, user["id"])
        all_coordinates = await project_embeddings([json.loads(concept["embedding"]) for concept in concepts], dimensions)
        all_concepts = [
            ConceptNode(
                id=concept["id"],
                topic_id=concept["topic_id"],
                coordinates=all_coordinates[id],
                text_length=concept["text_length"]
            ) for id, concept in enumerate(concepts)
        ]

        logger.info(f"Extracted {len(all_concepts)} concept nodes")

        return NodeResponse(
            nodes=all_concepts
        )

    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting node metadata: {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/node/{concept_id}", response_model=NodeDetailResponse)
async def get_node_detail(
    concept_id: int,
    db: Session = Depends(get_db)
):
    """API Route for extracting specific concept node data from backend

    Input:

    Ouput:
    """
    try:
        concept = get_concept_by_id(db, concept_id)

        if not concept:
            raise HTTPException(
                status_code=404,
                detail="Concept not found"
            )
        
        concept = concept[0]

        return NodeDetailResponse(
            id=concept["id"],
            concept=concept["name"],
            text=concept["raw_text"]
        )
    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting node internal data due to {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/relations", response_model=RelationResponse)
async def get_universe_relations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for extracting all relations from backend to populate universe

    Input:

    Ouput:
    """
    try:
        logger.info(f"Extracting all relations for user '{user["username"]}'")
        relations = get_all_relations_by_user_id(db, user["id"])

        all_relations = [
            RelationEdge(
                id=relation["relation_id"],
                source_id=relation["source_id"],
                target_id=relation["target_id"],
                name=relation["name"],
                explanation=relation["explanation"],
                weight=relation["weight"]
            ) for relation in relations
        ]

        return RelationResponse(
            edges=all_relations
        )

    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting relations for universe: {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/relation/{relation_id}", response_model=RelationDetailResponse)
async def get_relation_detail(
    relation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """API Route for extracting specific details for a relation edge

    Input:

    Ouput:
    """
    try:
        logger.info(f"Extracting relation information for relation id '{relation_id}'")
        relation = get_relation_by_id(db, relation_id)

        if not relation:
            raise HTTPException(
                status_code=404,
                detail="Relation not found"
            )
        
        relation = relation[0]

        return RelationDetailResponse(
            id=relation["id"],
            name=relation["name"],
            weight=relation["weight"],
            description=relation["description"],
            explanation=relation["explanation"]
        )

    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting relations for universe: {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )