from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    """
    Schema for Document table in db
    """
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    raw_text = Column(Text)
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