from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.operations import get_concepts_by_ids
from app.services.relationship import generate_relationships

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


def run_relationship_pipeline(concept_ids: list[int], user_id: int) -> None:
    """Background pipeline to generate relationships for a list of concept IDs

    Input:

    Output:
    """
    db: Session = get_db()

    try:
        # Re-fetch concepts from DB using the IDs passed in
        # Don't pass ORM objects across async boundaries — they may be detached
        concepts = get_concepts_by_ids(db, concept_ids)

        if not concepts:
            logger.warning(
                f"Relationship pipeline: no concepts found for IDs {concept_ids}"
            )
            return

        generate_relationships(
            db=db,
            concepts=concepts,
            user_id=user_id,
        )

    except Exception as e:
        logger.error(f"Relationship pipeline failed for user {user_id}: {e}")

    finally:
        db.close()  # Always close — this session is pipeline-owned