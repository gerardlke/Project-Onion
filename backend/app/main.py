from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import (
    engine, 
    Base
)
from app.logging import setup_logger
from app.routes import (
    upload,
    universe,
    user
)

from app.configs.config import RESET_DB

### Application Lifespan ==================================

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager to initialise shared resources
    - database connections
    - embedding models
    - vector indices
    - caches
    """

    logger.info("Starting backend...")

    # TODO: Load things needed in backend
    # app.state.embedding_model = load_embedding_model()
    
    # Setting up database
    logger.info("Starting database...")
    if RESET_DB:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield
    logger.info("Shutting down backend...")

app = FastAPI(
    title="Project Onion Backend",
    description="AI-Augmented Knowledge Cartography Backend",
    version="0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### Routes ================================================

@app.get("/")
async def root():
    return {
        "message": "Backend is running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }

app.include_router(
    upload.router,
    prefix="/upload",
    tags=["Upload"]
)

app.include_router(
    universe.router,
    prefix="/universe",
    tags=["Universe"]
)

app.include_router(
    user.router,
    prefix="/users",
    tags=["Users"]
)