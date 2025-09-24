"""
Floww Virtuals ACP - FastAPI backend for Virtuals platform integration.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.api.virtuals import adapter as virtuals_adapter

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include Virtuals adapter router
app.include_router(virtuals_adapter.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Floww Virtuals ACP Integration",
        "version": settings.VERSION,
        "status": "healthy",
        "endpoints": {
            "unified_request": "POST /api/virtuals/request",
            "agents": "GET /api/virtuals/agents",
            "status": "GET /api/virtuals/status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "floww-virtuals-acp",
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )