from sqlalchemy.orm import Session

from app.schemas.upload import PipelineDocument
from app.db.models import (
    Users,
    Topics,
    Documents,
    DocumentsToConcepts
    Concepts,
    Relations,
    RelationTypes
)


### Helper functions ==================================

def insert_row(db: Session, entry):
    """Helper function to insert new entry into db then return refreshed entry

    Input:

    Output:
    """
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def insert_batch(db: Session, entries):
    """Helper function to insert batch of entries into db then return refreshed entries

    Input:

    Output:
    """
    db.add_all(entries)
    db.commit()
    return entries


### Administrative queries ============================

def reset_database(db: Session):
    """Clears all rows from the database tables without destroying schema structures

    Input:

    Output:
    """
    try:
        db.query(Users).delete()
        db.query(Topics).delete()
        db.query(Documents).delete()
        db.query(DocumentsToConcepts).delete()
        db.query(Concepts).delete()
        db.query(Relations).delete()
        db.query(RelationTypes).delete()
        
        db.commit()
        return {"success": True, "detail": "Database contents successfully cleared."}
    
    except Exception as e:
        db.rollback()
        return {"success": False, "detail": f"Database reset failed: {str(e)}"}


### Users queries =====================================

def create_user(db: Session, username: str, password_hash: str):
    """Database operation to create a user in Users table

    Input:

    Ouput:
    """
    user = Users(
        username=username
        password_hash=password_hash
    )
    return insert_row(db, user)

def get_user_by_username(db: Session, username: str):
    """Database operation to get a user in Users table via username

    Input:

    Ouput:
    """
    return (
        db.query(Users)
        .filter(Users.username == username)
        .first()
    )

def get_user_by_id(db: Session, id: int):
    """Database operation to get a user in Users table via id

    Input:

    Ouput:
    """
    return (
        db.query(Users)
        .filter(Users.id == id)
        .first()
    )


### Topics queries ====================================

def create_topic(db: Session, user_id: int, name: str, description: str):
    """Database operation to create a topic in Topics table

    Input:

    Ouput:
    """
    topic = Topics(
        user_id=user_id,
        name=name,
        description=description
    )
    return insert_row(db, topic)

def get_topic_by_name(db: Session, name: str):
    """Database operation to retrieve a topic by its name

    Input:

    Ouput:
    """
    return (
        db.query(Topics)
        .filter(Topics.name == name)
        .first()
    )

def get_all_topics_by_userid(db: Session, user_id: int):
    """Database operation to retrieve all topics for a given user

    Input:

    Ouput:
    """
    return (
        db.query(Topics)
        .filter(Topics.user_id == user_id)
        .all()
    )


### Documents queries =================================

def create_document(db: Session, topic_id: int, filename: str, content_type: str, raw_text: str):
    """Database operation to create a new entry in Documents table

    Input:

    Ouput:
    """
    document = Document(
        topic_id=topic_id,
        filename=filename,
        content_type=content_type,
        raw_text=raw_text
    )
    return insert_row(db, document)


### DocumentsToConcepts queries =======================

def create_batch_document_to_concept(db: Session, document_id: int, concept_ids: list):
    """Database operation to insert a batch of DocumentsToConcepts relations in table

    Input:

    Ouput:
    """
    entries = []
    for concepts_id in concepts_ids:
        entries.append(
            DocumentsToConcepts(
                document_id=document_id,
                concept_id=concept_id
            )
        )
    return insert_batch(db, entries)


### Concepts queries ==================================

def create_batch_concept(db: Session, document_id: int, concepts: list, embeddings: list):
    """Database operation to insert a batch of entries in Concepts table

    Input:

    Ouput:
    """
    entries = []
    for concept, embedding in zipped(concepts, embeddings):
        entries.append(
            Concept(
                document_id=document_id,
                concept=concept,
                embedding=embedding
            )
        )
    return insert_batch(db, entries)

def get_all_concepts(db: Session):
    """Database operation to get all unique concepts from Concept table

    Input:

    Ouput:
    """
    return db.query(Concept).all()

def get_all_concepts_by_userid(db: Session, userid: int):
    """Database operation to get all unique concepts from Concept table

    Input:

    Ouput:
    """
    return (
        db.query(Concept)
        .filter()
    )

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


### Relations queries =======================

def create_relation(db: Session, source_id: int, target_id: int, relation_type: int, weight: float = 1.0):
    """Database operation to create a new relation between concepts in Relations table

    Input:

    Ouput:
    """
    relation = Relations(
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type,
        weight=weight
    )
    return insert_row(db, relation)


### RelationTypes queries =======================

def create_relation_type(db: Session, name: str, description: str):
    """Database operation to create a new relation type in RelationTypes table

    Input:

    Ouput:
    """
    relation_type = RelationTypes(
        name=name,
        description=description
    )
    return insert_row(db, relation_type)