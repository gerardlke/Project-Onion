from sqlalchemy import text
from sqlalchemy.orm import Session


### Helper functions ==================================

def execute_insert(db: Session, query_str: str, params: dict):
    """Helper function to insert new entry into db then return refreshed entry

    Input:

    Output:
    """
    result = db.execute(text(f"{query_str} RETURNING *"), params)
    db.commit()
    return result.mappings().first()

def execute_batch_insert(db: Session, query_str: str, params_list: list):
    """Helper function to insert batch of entries into db then return refreshed entries

    Input:

    Output:
    """
    if not params_list:
        return []
    db.execute(text(f"{query_str}"), params_list)
    db.commit()
    return []

def execute_select(db: Session, query_str: str, params: dict={}):
    """Helper function to select rows db

    Input:

    Output:
    """
    return db.execute(text(query_str), params).mappings().all()


### Administrative queries ============================

def reset_database(db: Session):
    """Clears all rows from the database tables without destroying schema structures

    Input:

    Output:
    """
    try:
        db.execute(text("TRUNCATE TABLE relations, relation_types, concepts, documents, topics, users CASCADE;"))
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
    query = """
        INSERT INTO users (username, password_hash) 
        VALUES (:username, :password_hash)
    """
    return execute_insert(db, query, {"username": username, "password_hash": password_hash})

def get_user_by_username(db: Session, username: str):
    """Database operation to get a user in Users table via username

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM users 
        WHERE username = :username
    """
    return execute_select(db, query, {"username": username})

def get_user_by_id(db: Session, id: int):
    """Database operation to get a user in Users table via id

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM users 
        WHERE id = :id
    """
    return execute_select(db, query, {"id": id})


### Topics queries ====================================

def create_topic(db: Session, user_id: int, name: str, description: str):
    """Database operation to create a topic in Topics table

    Input:

    Ouput:
    """
    query = """
        INSERT INTO topics (user_id, name, description) 
        VALUES (:user_id, :name, :description)
    """
    params = {"user_id": user_id, "name": name, "description": description}
    return execute_insert(db, query, params)

def get_topic_by_name(db: Session, name: str):
    """Database operation to retrieve a topic by its name

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM topics 
        WHERE name = :name
    """
    return execute_select(db, query, {"name": name})

def get_all_topics_by_user_id(db: Session, user_id: int):
    """Database operation to retrieve all topics for a given user

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM topics 
        WHERE user_id = :user_id
    """
    return execute_select(db, query, {"user_id": user_id})

def get_topic_by_document_id(db: Session, document_id: int):
    """Database operation to retrieve the topic of a given document via document id

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM topics
        INNER JOIN documents ON topics.id = documents.topic_id
        WHERE documents.id = :document_id
    """
    return execute_select(db, query, {"document_id": document_id})


### Documents queries =================================

def create_document(db: Session, topic_id: int, filename: str, content_type: str, raw_text: str):
    """Database operation to create a new entry in Documents table

    Input:

    Ouput:
    """
    query = """
        INSERT INTO documents (topic_id, filename, content_type, raw_text) 
        VALUES (:topic_id, :filename, :content_type, :raw_text)
    """
    params = {
        "topic_id": topic_id,
        "filename": filename,
        "content_type": content_type,
        "raw_text": raw_text
    }
    return execute_insert(db, query, params)


### Concepts queries ==================================

def create_batch_concept(db: Session, batch_concepts: list):
    """Database operation to insert a batch of entries in Concepts table

    Input:

    Ouput:
    """
    query = """
        INSERT INTO concepts (document_id, name, raw_text, embedding) 
        VALUES (:document_id, :name, :raw_text, :embedding)
    """
    return execute_batch_insert(db, query, batch_concepts)

def get_all_concepts(db: Session):
    """Database operation to get all unique concepts from Concept table

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM concepts
    """
    return execute_select(db, query)

def get_all_concepts_by_user_id(db: Session, user_id: int):
    """Database operation to get all unique concepts from Concept table

    Input:

    Ouput:
    """
    query = """
        SELECT concepts.id AS id, concepts.document_id AS document_id, concepts.embedding AS embedding
        FROM concepts
        INNER JOIN documents ON documents.id = concepts.document_id
        INNER JOIN topics ON topics.id = documents.topic_id
        WHERE topics.user_id = :user_id
    """
    return execute_select(db, query, {"user_id": user_id})

def get_concept_by_id(db: Session, concept_id: int):
    """Database operation to get a specific concept from Concept table

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM concepts 
        WHERE id = :concept_id
    """
    return execute_select(db, query, {"concept_id": concept_id})

def get_similar_concepts(db: Session, user_id: int, concept_id: int, embedding, threshold: float = 0.5, limit: int = 10):
    """Database operation to do similarity search on embeddings 

    Input:

    Ouput:
    """
    query = """
        WITH calculated_distances AS (
            SELECT
                id,
                concept,
                embedding <=> :embedding AS distance
            FROM concepts
            WHERE user_id = :user_id
                AND id != :concept_id
        )
        SELECT id, concept, distance
        FROM calculated_distances
        WHERE distance <= :distance_threshold
        ORDER BY distance ASC
        LIMIT :limit
    """
    params = {
        "embedding": embedding,
        "user_id": user_id,
        "concept_id": concept_id,
        "distance_threshold": threshold,
        "limit": limit
    }
    return execute_select(db, query, params)


### Relations queries =======================

def create_relation(db: Session, source_id: int, target_id: int, relation_type: int, weight: float = 1.0):
    """Database operation to create a new relation between concepts in Relations table

    Input:

    Ouput:
    """
    query = """
        INSERT INTO relations (source_id, target_id, relation_type, weight) 
        VALUES (:source_id, :target_id, :relation_type, :weight)
    """
    params = {
        "source_id": source_id,
        "target_id": target_id,
        "relation_type": relation_type,
        "weight": weight
    }
    return execute_insert(db, query, params)

def get_all_relations_by_user_id(db: Session, user_id: int):
    """Database operation to retrieve the all relations for all nodes given a user

    Input:

    Ouput:
    """
    query = """
        SELECT 
            relations.id AS relation_id AS relation_id,
            relations.source_id AS source_id,
            relations.target_id AS target_id,
            relation_types.name AS name
        FROM relations
        INNER JOIN relation_types ON relations.relation_type = relation_types.id
        INNER JOIN concepts ON relations.source_id = concepts.id
        INNER JOIN documents ON concepts.document_id = documents.id
        INNER JOIN topics ON documents.topic_id = topics.id
        WHERE topics.user_id = :user_id

        UNION

        SELECT 
            relations.id AS relation_id,
            relations.source_id AS source_id,
            relations.target_id AS target_id,
            relation_types.name AS name
        FROM relations
        INNER JOIN relation_types ON relations.relation_type = relation_types.id
        INNER JOIN concepts ON relations.target_id = concepts.id
        INNER JOIN documents ON concepts.document_id = documents.id
        INNER JOIN topics ON documents.topic_id = topics.id
        WHERE topics.user_id = :user_id
    """
    return execute_select(db, query, {"user_id": user_id})

def get_relation_by_id(db: Session, id: int):
    """Database operation to retrieve the all relations for all nodes given a user

    Input:

    Ouput:
    """
    query = """
        SELECT 
            relations.id AS id, 
            relation_types.name AS name,
            relation_types.description AS description,
            relations.explanation AS explanation
        FROM relations
        INNER JOIN relation_types ON relations.relation_type_id == relation_types.id
        WHERE relations.id == :id
    """
    return execute_select(db, query, {"id": id})


### Relation Types queries ======================

def create_relation_type(db: Session, name: str, description: str):
    """Database operation to create a new relation type in Relation Types table

    Input:

    Ouput:
    """
    query = """
        INSERT INTO relation_types (name, description) 
        VALUES (:name, :description)
    """
    return execute_insert(db, query, {"name": name, "description": description})

def get_all_relation_types(db: Session):
    """Database operation to retrieve all relation types

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM relation_types
    """
    return execute_insert(db, query)

def get_relation_type_by_id(db: Session, type_id: int):
    """Database operation to retrieve the relation type by its id

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM relation_types 
        WHERE id = :type_id
    """
    return execute_insert(db, query, {"type_id": type_id})