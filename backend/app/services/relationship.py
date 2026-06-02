from app.db.crud import (
    find_similar_concepts
)

def generate_relationships(
    db,
    concept,
    user_id
):
    similar_concepts = find_similar_concepts(
        db=db,
        embedding=concept.embedding,
        user_id=user_id,
        limit=5
    )
    create_relation(...)
    return similar_concepts