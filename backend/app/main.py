from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.routes as routes


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

    print("Starting backend...")

    # app.state.embedding_model = load_embedding_model()
    yield

    print("Shutting down backend...")

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
    routes.upload,
    prefix="/upload",
    tags=["Upload"]
)