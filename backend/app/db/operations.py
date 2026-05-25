from sqlalchemy.orm import Session

from app.schemas.upload import PipelineDocument
from app.schemas.database import (
    Document,
    Concept,
)


def create_document(
    db: Session,
    filename: str,
    raw_text: str
):
    """Database operation to create a new entry in document table

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


def create_concepts(
    db: Session,
    document_id: int,
    pipeline_document: PipelineDocument
):
    """Database operation to create a new entry in concepts table

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

# =====================================================
# GET ALL CONCEPT NODES
# =====================================================

def get_all_concepts(
    db: Session
):

    return db.query(Concept).all()


# =====================================================
# GET SINGLE CONCEPT
# =====================================================

def get_concept_by_id(
    db: Session,
    concept_id: int
):

    return (
        db.query(Concept)
        .filter(Concept.id == concept_id)
        .first()
    )