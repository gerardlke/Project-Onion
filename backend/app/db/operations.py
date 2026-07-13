from sqlalchemy import text
from sqlalchemy.orm import Session


### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)


### Helper functions ==================================

def execute_insert(db: Session, query_str: str, params: dict = {}):
    """Helper function to insert new entry into db then return refreshed entry

    Input:

    Output:
    """
    try:
        result = db.execute(text(f"{query_str} RETURNING *"), params)
        db.commit()
        return result.mappings().first()
    except Exception as e:
        db.rollback()
        logger.error(f"Insert failed: {e}")
        raise

def execute_batch_insert(db: Session, query_str: str, params_list: list):
    """Helper function to insert batch of entries into db then return refreshed entries

    Input:

    Output:
    """
    if not params_list:
        return []
    try:
        result = db.execute(text(query_str), params_list)
        rows = [dict(row) for row in result.mappings().all()]
        db.commit()
        return rows
    except Exception as e:
        db.rollback()
        logger.error(f"Batch insert failed: {e}")
        raise

def execute_select(db: Session, query_str: str, params: dict={}):
    """Helper function to select rows db

    Input:

    Output:
    """
    try:
        return db.execute(text(query_str), params).mappings().all()
    except Exception as e:
        db.rollback()
        logger.error(f"Select failed: {e}")
        raise

def execute_update(db: Session, query_str: str, params: dict = {}):
    """Helper function to update an entry in the db then return refreshed entry

    Input:

    Output:
    """
    try:
        result = db.execute(text(f"{query_str} RETURNING *"), params)
        db.commit()
        return result.mappings().first()
    except Exception as e:
        db.rollback()
        logger.error(f"Insert failed: {e}")
        raise

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

def get_topic_by_id(db: Session, id: int):
    """Database operation to retrieve a topic by its id

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM topics 
        WHERE id = :id
    """
    return execute_select(db, query, {"id": id})

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
        SELECT topics.id AS id, topics.name AS name, topics.description AS description
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


### Documents to Concepts queries =====================

def create_concept_to_document(db: Session, concept_id: int, document_id: int):
    """Record that a concept was sourced from a document
    """
    query = """
        INSERT INTO documents_to_concepts (concept_id, document_id)
        VALUES (:concept_id, :document_id)
        ON CONFLICT DO NOTHING
    """
    params = {"concept_id": concept_id, "document_id": document_id}
    return execute_insert(db, query, params)


### Concepts queries ==================================

def create_batch_concept(db: Session, batch_concepts: list):
    """Database operation to insert a batch of entries in Concepts table

    Input:

    Ouput:
    """
    if not batch_concepts:
        return []
    
    columns = ["user_id", "name", "raw_text", "embedding"]
    values, params = [], {}
    for i, concept in enumerate(batch_concepts):
        placeholders = ", ".join(f":{col}_{i}" for col in columns)
        values.append(f"({placeholders})")
        for col in columns:
            params[f"{col}_{i}"] = concept[col]

    query = f"""
        INSERT INTO concepts ({", ".join(columns)}) 
        VALUES {", ".join(values)}
        ON CONFLICT (user_id, name) DO UPDATE
            SET raw_text = concepts.raw_text || '. ' || EXCLUDED.raw_text
        RETURNING *, (xmax != 0) AS updated
    """
    return execute_batch_insert(db, query, params)

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
        SELECT DISTINCT ON (concepts.id)
            concepts.id AS id,
            concepts.user_id AS user_id,
            concepts.name AS name,
            concepts.embedding AS embedding,
            topics.id AS topic_id
        FROM concepts
        LEFT JOIN documents_to_concepts
            ON documents_to_concepts.concept_id = concepts.id
        LEFT JOIN documents
            ON documents.id = documents_to_concepts.document_id
        LEFT JOIN topics
            ON topics.id = documents.topic_id
        WHERE concepts.user_id = :user_id
        ORDER BY concepts.id
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

def get_concepts_by_names(db: Session, concepts: list[str]):
    """Database operation to get multiple concepts from Concept table by ID list

    Input:

    Output:
    """
    query = """
        SELECT *
        FROM concepts
        WHERE name = ANY(:concepts)
    """
    return execute_select(db, query, {"concepts": concepts})

def get_similar_concepts_by_concept_id(db: Session, user_id: int, concept_id: int, embedding, threshold: float = 0.5, limit: int = 10):
    """Database operation to do similarity search on embeddings based on a stored concept

    Input:

    Ouput:
    """
    query = """
        WITH calculated_distances AS (
            SELECT
                id,
                name,
                raw_text,
                embedding <=> CAST(:embedding AS vector) AS distance
            FROM concepts
            WHERE user_id = :user_id
                AND id != :concept_id
        )
        SELECT id, name, raw_text, distance
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

def search_concepts_by_embedding(db: Session, user_id: int, query_embedding: list[float], limit: int = 5, distance_threshold: float = 0.6):
    """Database operation to retrieve concepts semantically similar to a query embedding
    
    Input:
    
    Output:
    """
    query = """
        WITH ranked AS (
            SELECT
                id,
                name,
                raw_text,
                embedding <=> CAST(:query_embedding AS vector) AS distance
            FROM concepts
            WHERE user_id = :user_id
        )
        SELECT id, name, raw_text, distance
        FROM ranked
        WHERE distance <= :distance_threshold
        ORDER BY distance ASC
        LIMIT :limit
    """
    params = {
        "query_embedding": query_embedding,
        "user_id": user_id,
        "distance_threshold": distance_threshold,
        "limit": limit
    }
    return execute_select(db, query, params)

def update_concept_embedding(db: Session, concept_id: int, embedding: list):
    """Update the embedding for a concept after its raw_text was merged

    Input:
        concept_id: id of the concept to update
        embedding: newly generated embedding vector

    Output: updated concept row
    """
    query = """
        UPDATE concepts
        SET embedding = :embedding
        WHERE id = :concept_id
    """
    params = {"concept_id": concept_id, "embedding": embedding}
    return execute_update(db, query, params)
        

### Relations queries =======================

def create_relation(db: Session, source_id: int, target_id: int, relation_type_id: int, weight: float = 1.0, explanation: str = ""):
    """Database operation to create a new relation between concepts in Relations table

    Input:

    Ouput:
    """
    query = """
        INSERT INTO relations (source_id, target_id, relation_type_id, weight, explanation) 
        VALUES (:source_id, :target_id, :relation_type_id, :weight, :explanation)
    """
    params = {
        "source_id": source_id,
        "target_id": target_id,
        "relation_type_id": relation_type_id,
        "weight": weight,
        "explanation": explanation
    }
    return execute_insert(db, query, params)

def get_all_relations_by_user_id(db: Session, user_id: int):
    """Database operation to retrieve the all relations for all nodes given a user

    Input:

    Ouput:
    """
    query = """
        SELECT DISTINCT
            relations.id AS relation_id,
            relations.source_id,
            relations.target_id,
            rt.name
        FROM relations
        JOIN relation_types rt ON relations.relation_type_id = rt.id
        JOIN concepts sc ON relations.source_id = sc.id
        JOIN concepts tc ON relations.target_id = tc.id
        WHERE sc.user_id = :user_id
           OR tc.user_id = :user_id
    """
    return execute_select(db, query, {"user_id": user_id})

def get_relation_by_id(db: Session, id: int):
    """Database operation to retrieve a specific relation by its id

    Input:

    Ouput:
    """
    query = """
        SELECT 
            relations.id AS id, 
            relation_types.name AS name,
            relations.weight AS weight,
            relation_types.description AS description,
            relations.explanation AS explanation
        FROM relations
        INNER JOIN relation_types ON relations.relation_type_id = relation_types.id
        WHERE relations.id = :id
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
    return execute_select(db, query)

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
    return execute_select(db, query, {"type_id": type_id})

def get_relation_type_by_name(db: Session, name: str):
    """Database operation to retrieve the relation type by its name

    Input:

    Ouput:
    """
    query = """
        SELECT * 
        FROM relation_types 
        WHERE name = :name
    """
    return execute_select(db, query, {"name": name})