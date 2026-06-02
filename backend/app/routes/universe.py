from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.logging import setup_logger
from app.pipelines.authentication_pipeline import get_current_user
from app.db.session import get_db
from app.db.operations import (
    get_all_concepts_by_userid,
    get_concept_by_id
)
from app.schemas.universe import (
    TopicResponse,
    UniverseNode,
    NodeResponse,
    NodeDetailResponse,
    RelationResponse
)


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()


@router.get("/topics", response_model=TopicResponse)
async def get_universe_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API Route for extracting all topics from backend

    Input:

    Ouput:
    """
    try:
        logger.info("Extracting topics.")

        return TopicResponse(
        )

    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting topics for universe: {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/nodes", response_model=UniverseResponse)
async def get_universe_nodes(
    dimensions: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API Route for extracting concept nodes from backend

    Input:

    Ouput:
    """
    try:
        logger.info("Extracting concept nodes.")

        # Extract key node metadata from db
        nodes = []  
        for concept in get_all_concepts_by_userid(db, user.id):

            nodes.append(
                UniverseNode(
                    id=concept.id,
                    concept=concept.concept,
                    frequency=concept.frequency,

                    x=concept.x,
                    y=concept.y,
                    z=concept.z
                )
            )

        return UniverseResponse(
            nodes=nodes
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
    """API Route for extracting concept node data from backend

    Input:

    Ouput:
    """
    try:
        concept = get_concept_by_id(
            db,
            concept_id
        )

        if not concept:
            raise HTTPException(
                status_code=404,
                detail="Concept not found"
            )

        return NodeDetailResponse(
            id=concept.id,
            concept=concept.concept,
            frequency=concept.frequency,
            chunk_index=concept.chunk_index,

            x=concept.x,
            y=concept.y,
            z=concept.z,

            document_id=concept.document_id
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
async def get_universe_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API Route for extracting all relations from backend

    Input:

    Ouput:
    """
    try:
        logger.info("Extracting relations.")

        return RelationResponse(
        )

    except Exception as error:
        logger.exception(
            f"Unexpected error while extracting relations for universe: {error}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )