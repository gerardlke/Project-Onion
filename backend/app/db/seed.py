from sqlalchemy.orm import Session

from app.db.operations import (
    get_all_relation_types, 
    create_relation_type
)

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


RELATION_TYPES = [
    {"name": "SIMILAR", "description": "these concepts are very similar or overlap significantly"},
    {"name": "PREREQUISITE", "description": "the first concept is a prerequisite for understanding the second"},
    {"name": "PART_OF", "description": "the first concept is a component or part of the second concept"},
    {"name": "APPLICATION_OF", "description": "the first concept is a practical application of the second"},
    {"name": "ALIAS", "description": "these concepts are different names for the same idea"},
    {"name": "CONTRASTS", "description": "these concepts contrast or differ despite surface similarity"},
]


def seed_relation_types(db: Session):
    """Insert default relation types if they don't already exist"""

    existing = get_all_relation_types(db)
    existing_names = {r["name"] for r in existing}

    to_insert = [r for r in RELATION_TYPES if r["name"] not in existing_names]

    if not to_insert:
        logger.info("Relation types already seeded - skipping")
        return

    for relation_type in to_insert:
        create_relation_type(db, relation_type["name"], relation_type["description"])

    logger.info(f"Seeded {len(to_insert)} relation type(s): {[r['name'] for r in to_insert]}")