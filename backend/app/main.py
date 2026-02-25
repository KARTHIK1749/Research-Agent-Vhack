"""
FastAPI main application entry point.
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 AI Research Co-Scientist starting up...")
    yield
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="AI Research Co-Scientist",
    description="Multi-agent system for automated research workflow",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api", tags=["research"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-research-co-scientist"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI Research Co-Scientist",
        "version": "1.0.0",
        "endpoints": {
            "start_research": "POST /api/research/start",
            "research_step": "POST /api/research/step",
            "get_state": "GET /api/research/state",
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
