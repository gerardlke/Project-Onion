from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.operations import get_concepts_by_names
from app.services.relationship import generate_relationships

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


def run_relationship_pipeline(concept_names: list[str], user_id: int) -> None:
    """Background pipeline to generate relationships for a list of concept IDs

    Input:

    Output:
    """
    db: Session = SessionLocal()

    try:
        # Re-fetch concepts from DB using the names passed in
        concepts = get_concepts_by_names(db, concept_names)

        if not concepts:
            logger.warning(
                f"Relationship pipeline: no concepts found for names '{concept_names}'"
            )
            return
        
        logger.info(f"Starting relationship pipeline for user {user_id} with {len(concepts)} concept(s)")

        generate_relationships(
            db=db,
            concepts=concepts,
            user_id=user_id,
        )

    except Exception as e:
        logger.error(f"Relationship pipeline failed for user {user_id}: {e}")

    finally:
        db.close()