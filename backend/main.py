"""
Main FastAPI application for B2B lead generation platform.

WHAT: FastAPI application providing REST API endpoints for lead generation,
      reference client management, campaign organization, and prospect tracking.

WHY: Provides a complete web application interface for sales teams to discover,
     organize, and track potential business prospects using geographic and
     business similarity matching.

HOW: Uses FastAPI with async/await, integrates with PostgreSQL database,
     implements password-only authentication, and provides JSON APIs for
     all lead generation functionality.

DEPENDENCIES:
- fastapi: Web framework and HTTP handling
- uvicorn: ASGI server for running the application
- backend.database: Database configuration and models
- backend.auth: Authentication middleware
- backend.api: Route handlers for all endpoints
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.database.config import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown tasks.
    
    Handles database initialization during startup and cleanup
    during shutdown.
    """
    # Startup: Initialize database tables
    try:
        print("🔧 Initializing database connection...")
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  Application will start but database features may not work")
        # Don't fail startup - let the app start even if DB is not ready
    
    yield
    
    # Shutdown: Cleanup tasks
    print("👋 Application shutting down")


# Create FastAPI application
app = FastAPI(
    title="LookLike Nearby - Lead Generation Platform",
    description="B2B referral lead generation platform for finding similar businesses",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
origins = [
    "http://localhost:3000",  # Next.js dev server
    "https://*.vercel.app",   # Vercel preview deployments
    "https://*.vercel.com",   # Vercel production deployments
    os.getenv("FRONTEND_URL", "http://localhost:3000"),  # Environment-based URL
]

# Allow all origins in development
if os.getenv("DEBUG", "false").lower() == "true":
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, images)
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.
    
    Provides consistent error responses and prevents sensitive
    information from leaking in production.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred"
        }
    )


@app.get("/")
async def root() -> dict:
    """Root endpoint providing API information."""
    return {
        "message": "LookLike Nearby - Lead Generation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "looklike-nearby"}


@app.get("/app")
async def serve_app() -> FileResponse:
    """Serve the main application HTML page."""
    return FileResponse("frontend/templates/index.html")


# Include API routes
from backend.api import (
    auth_router,
    campaigns_router,
    prospects_router,
    reference_clients_router,
    search_router,
)
from backend.api.stats import router as stats_router

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(reference_clients_router, prefix="/api/reference-clients", tags=["reference-clients"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(prospects_router, prefix="/api/prospects", tags=["prospects"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(stats_router, prefix="/api/stats", tags=["stats"])


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 