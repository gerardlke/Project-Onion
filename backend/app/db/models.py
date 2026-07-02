from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    UniqueConstraint
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
    topics = relationship(
        "Topics",
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Topic information
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Table relations
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="topics_user_name_unique"),
    )

    users = relationship(
        "Users",
        back_populates="topics"
    )
    documents = relationship(
        "Documents",
        back_populates="topics",
        cascade="all, delete"
    )


class Documents(Base):
    """
    Schema for Documents table in db, 
    many-to-one relationship with Topics
    many-to-many relationship with Concepts
    """
    __tablename__ = "documents"

    # Metadata
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)

    # Document information
    filename = Column(String, nullable=False)
    content_type = Column(String)
    raw_text = Column(Text)

    # Table relationships
    topics = relationship(
        "Topics",
        back_populates="documents"
    )

    concepts = relationship(
        "Concepts", 
        secondary="documents_to_concepts",
        back_populates="documents",
    )


class Documents_To_Concepts(Base):
    """
    Schema for Documents to Concepts junction table in db, 
    one-to-many relationship with Documents,
    one-to-many relationship with Concepts
    """
    __tablename__ = "documents_to_concepts"

    # Metadata
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True
    )
    concept_id  = Column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True
    )


class Concepts(Base):
    """
    Schema for Concepts table in db, 
    many-to-many relationship with Documents
    one-to-many relationship with Relations
    """
    __tablename__ = "concepts"

    # Metadata
    id = Column(Integer, primary_key=True)
    chunk_index = Column(Integer)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Concept information
    name = Column(String, nullable=False)
    raw_text = Column(String, nullable=False)
    embedding = Column(Vector(384), nullable=False)

    # Table relationships 
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="concepts_user_name_unique"),
    )

    user = relationship(
        "Users",
        back_populates="concepts"
    )
    documents = relationship(
        "Documents",
        secondary="documents_to_concepts",
        back_populates="concepts",
    )

    outgoing_relations = relationship(
        "Relations", 
        foreign_keys="[Relations.source_id]", 
        back_populates="source_concept",
        cascade="all, delete"
    )
    incoming_relations = relationship(
        "Relations", 
        foreign_keys="[Relations.target_id]", 
        back_populates="target_concept",
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
    source_concept = relationship(
        "Concepts",
        foreign_keys=[source_id]
    )
    target_concept = relationship(
        "Concepts",
        foreign_keys=[target_id]
    )
    relation_type = relationship(
        "RelationTypes",
        back_populates="relations"
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
        back_populates="relation_type",
        cascade="all, delete"
    )