from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.database import Base


class Users(Base):
    """
    Schema for Users table in db, 
    one-to-many relationship with Documents
    """
    __tablename__ = "users"

    # Metadata
    id = Column(Integer, primary_key=True)

    # User information
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Table relationships 
    documents = relationship(
        "Documents",
        back_populates="users",
        cascade="all, delete"
    )


class Topics(Base):
    """
    Schema for Topics table in db,
    one-to-many relationship with Documents
    """
    __tablename__ = "topics"

    # Metadata
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Topic information
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    
    # Table relations
    documents = relationship(
        "Documents",
        back_populates="topics",
        cascade="all, delete"
    )


class Documents(Base):
    """
    Schema for Documents table in db, 
    one-to-many relationship with Concepts
    """
    __tablename__ = "documents"

    # Metadata
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))

    # Document information
    filename = Column(String, nullable=False)
    content_type = Column(String)
    raw_text = Column(Text)

    # Table relationships 
    users = relationship(
        "Users",
        back_populates="documents"
    )

    topics = relationship(
        "Topics",
        back_populates="documents"
    )

    concepts = relationship(
        "Concepts",
        back_populates="documents",
        cascade="all, delete"
    )


class Concepts(Base):
    """
    Schema for Concepts table in db, 
    many-to-one relationship with Documents
    one-to-many relationship with Relations
    """
    __tablename__ = "concepts"

    # Metadata
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)

    # Concept information
    name = Column(String, nullable=False)
    raw_text = Column(String, nullable=False)
    embedding = Column(Vector(384), nullable=False)

    # Table relationships 
    documents = relationship(
        "Documents",
        back_populates="concepts"
    )

    relations = relationship(
        "Relations",
        back_populates="concepts",
        cascade="all, delete"
    )


class Relations(Base):
    """
    Schema for Relations table in db, 
    many-to-one relationship with RelationTypes
    """
    __tablename__ = "relations"
    
    # Metadata
    id = Column(Integer, primary_key=True)

    # Concept to concept relationship
    source_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    relation_type_id = Column(Integer, ForeignKey("relation_types.id"), nullable=False)

    # Relation information
    weight = Column(Float)
    explanation = Column(String)

    # Table relationships 
    source_concepts = relationship(
        "Concepts",
        foreign_keys=[source_id]
    )

    target_concepts = relationship(
        "Concepts",
        foreign_keys=[target_id]
    )


class RelationTypes(Base):
    """
    Schema for Relation Types table in db
    """
    __tablename__ = "relation_types"

    # Metadata
    id = Column(Integer, primary_key=True)

    # RelationType information
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Table relationships 
    relations = relationship(
        "Relations",
        back_populates="relation_types",
        cascade="all, delete"
    )