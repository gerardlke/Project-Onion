from app.db.operations import (
    get_all_relation_types,
    get_similar_concepts,
    create_relation
)

### Set up configs
from app.configs.config import (
    SIMILARITY_THRESHOLD,
    RELATIONSHIP_LIMIT
)


def generate_relationships(db, concept, user_id):
    """Helper funciton to generate relationships for each uploaded concept

    Input:

    Ouput:
    """
    # Get all relationship types for matching later
    relation_types = get_all_relation_types()

    # For each concept get their similar concepts
    similar_concepts = get_similar_concepts(
        db=db,
        user_id=user_id,
        concept_id=concept["id"],
        embedding=concept["embedding"],
        threshold=SIMILARITY_THRESHOLD,
        limit=RELATIONSHIP_LIMIT
    )

    # For each similar concept, identify and create the type of relationship
    for neighbour in similar_concepts:
        # TODO: Classify relationship type here
        # relation_type = classify_relation()
        relation_type = {}

        create_relation(
            db=db,
            source_id=concept["id"],
            target_id=neighbour["id"],
            relation_type=relation_type["id"],
            weight=1.0-neighbour["distance"]
        )

    return similar_concepts