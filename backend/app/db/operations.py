from sqlalchemy.orm import Session

from app.schemas.upload import PipelineDocument
from app.db.models import (
    User,
    Document,
    Concept,
)


### User queries ======================================

def get_user_by_username(db: Session, username: str):
    """Database operation to get a user in User table via username

    Input:

    Ouput:
    """
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

def create_user(db: Session, username: str):
    """Database operation to create a user in User table

    Input:

    Ouput:
    """
    user = User(
        username=username
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


### Document queries ==================================

def create_document(db: Session, filename: str, raw_text: str):
    """Database operation to create a new entry in Document table

    Input:

    Ouput:
    """
    document = Document(
        filename=filename,
        raw_text=raw_text
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


### Concept queries ===================================

def create_concepts(db: Session, document_id: int, pipeline_document: PipelineDocument):
    """Database operation to create a new entry in Concept table

    Input:

    Ouput:
    """
    entries = []
    for concept in pipeline_document.concepts:
        entries.append(
            Concept(
                document_id=document_id,
                concept=concept.concept,
                frequency=concept.frequency,
                x=concept.x,
                y=concept.y,
                z=concept.z
            )
        )

    db.add_all(entries)
    db.commit()
    return entries

def get_all_concepts(db: Session):
    """Database operation to get all unique concepts from Concept table

    Input:

    Ouput:
    """
    return db.query(Concept).all()

def get_concept_by_id(db: Session, concept_id: int):
    """Database operation to get a specific concept from Concept table

    Input:

    Ouput:
    """
    return (
        db.query(Concept)
        .filter(Concept.id == concept_id)
        .first()
    )