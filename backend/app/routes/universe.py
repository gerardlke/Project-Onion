from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.db.session import get_db
from app.db.operation import (
    get_all_concepts,
    get_concept_by_id
)
from app.schemas.universe import (
    UniverseNode,
    UniverseResponse,
    NodeDetailResponse
)


### Set up API and logger
logger = setup_logger(__name__)
router = APIRouter()

@router.get("/nodes", response_model=UniverseResponse)
async def get_universe_nodes(
    db: Session = Depends(get_db)
):
    """API Route for extracting concept nodes from backend

    Input:

    Ouput:
    """
    try:
        logger.info("Extracting concept nodes.")

        # Extract key node metadata from db
        nodes = []
        for concept in get_all_concepts(db):

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
            f"Unexpected error while extracting node metadata"
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
            f"Unexpected error while extracting node internal data"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )