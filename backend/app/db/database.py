import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)
from sqlalchemy_utils import database_exists, create_database

from app.logging import setup_logger


### Set up logger
logger = setup_logger(__name__)


### Set up database engine
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Turned off to reduce log confusion
)

with engine.connect() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    connection.commit()

# Check if database already exists
if not database_exists(engine.url):
    create_database(engine.url)
    logger.info("Database created successfully.")
else:
    logger.info("Database already exists.")

Base = declarative_base()

### Import database models
from app.db.models import (
    Users, Topics, Documents, Concepts, Relations, RelationTypes
)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)