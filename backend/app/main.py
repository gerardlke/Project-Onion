from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import (
    engine, 
    SessionLocal,
    Base
)
from app.db.seed import seed_relation_types
from app.routes import (
    admin,
    upload,
    universe,
    user
)

# Warm up from llm and relationship service
from app.services.llm import warm_up
from app.services.relationship import _get_nli

### Set up configs
from app.configs.config import RESET_DB

### Set up logger
from app.logging import setup_logger
logger = setup_logger(__name__)

### Application Lifespan ==================================

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
    
    # Setting up database
    logger.info("Starting database...")
    if RESET_DB:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed static data
    logger.info("Seeding database...")
    db = SessionLocal()
    try:
        seed_relation_types(db)
    finally:
        db.close()
    
    # Loading models
    # logger.info("Warming up ML models...")
    # _get_nli()
    # await warm_up()

    logger.info("Backend started")

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
    allow_origins=["*", "http://localhost:3000"],  # TODO: tighten later
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
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)

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
    prefix="/user",
    tags=["User"]
)