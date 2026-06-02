from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """
    Schema for User table in db, one-to-many relationship with Documents
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete"
    )


class Document(Base):
    """
    Schema for Document table in db, many-to-many relationship with Concepts
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    content_type = Column(String)
    raw_text = Column(Text)

    user = relationship(
        "User",
        back_populates="documents"
    )

    concepts = relationship(
        "Concept",
        back_populates="document",
        cascade="all, delete"
    )


class Concept(Base):
    """
    Schema for Concept table in db
    """
    __tablename__ = "concepts"

    # Metadata
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    concept = Column(String, nullable=False)
    frequency = Column(Integer)

    # Vector coordinates
    x = Column(Float)
    y = Column(Float)
    z = Column(Float, nullable=True)

    document = relationship(
        "Document",
        back_populates="concepts"
    )