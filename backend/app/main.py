"""
Main FastAPI application.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import clients, onboarding, webhooks
from app.core.config import settings
import logging
import time

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Silence uvicorn access logs for health checks
logging.getLogger("uvicorn.access").addFilter(
    lambda record: "/health" not in record.getMessage()
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered client onboarding system for GoHighLevel agencies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (no prefix needed, DO routes /api to this service)
app.include_router(clients.router)
app.include_router(onboarding.router)
app.include_router(webhooks.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GHL Healthcare Onboarding System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.environment == "development"
    )
