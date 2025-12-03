"""
FastAPI application for Discord Bot Web UI
Modern async API to replace Flask
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import (
    WEB_ENABLED,
    WEB_PORT,
    WEB_HOST,
    WEB_AUTH_ENABLED,
    WEB_SECRET_KEY,
    WEB_VERBOSE_LOGGING,
)

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "api.log")

logging.basicConfig(
    level=logging.DEBUG if WEB_VERBOSE_LOGGING else logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Bot instance (set by main bot.py)
bot_instance = None


def set_bot_instance(bot):
    """Set the Discord bot instance for API access"""
    global bot_instance
    bot_instance = bot
    logger.info("Bot instance set for API")


def get_bot_instance():
    """Get the Discord bot instance"""
    return bot_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("FastAPI starting up...")
    yield
    logger.info("FastAPI shutting down...")


# Initialize FastAPI
app = FastAPI(
    title="Discord Bot API",
    description="Modern async API for Discord bot management",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if WEB_VERBOSE_LOGGING else None,
    redoc_url="/api/redoc" if WEB_VERBOSE_LOGGING else None,
)

# CORS middleware - configure for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Production + Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routers
from api.routers import (
    auth,
    dashboard,
    settings,
    tickets,
    invites,
    databases,
    services,
    members,
    commands,
    guild_stats,
    about,
    websocket,
)

# Register API routers FIRST (before catch-all routes)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(invites.router, prefix="/api/invites", tags=["Invites"])
app.include_router(databases.router, prefix="/api/databases", tags=["Databases"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(members.router, prefix="/api/members", tags=["Members"])
app.include_router(commands.router, prefix="/api/commands", tags=["Commands"])
app.include_router(guild_stats.router, prefix="/api/guild-stats", tags=["Guild Stats"])
app.include_router(about.router, prefix="/api/about", tags=["About"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot_connected": (
            bot_instance is not None and bot_instance.is_ready()
            if bot_instance
            else False
        ),
    }


# Serve static files from frontend/dist
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount(
        "/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets"
    )
    logger.info(f"Serving static files from {frontend_dist}")


# Frontend routes LAST (after all API routes)
@app.get("/")
async def serve_frontend():
    """Serve the React frontend"""
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(
        status_code=404,
        content={
            "error": "Frontend not built. Run 'npm run build' in frontend directory"
        },
    )


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Catch-all route for SPA routing - MUST BE LAST"""
    # Don't catch API routes (shouldn't happen if API routes are defined first)
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        return JSONResponse(
            status_code=404, content={"error": "API endpoint not found"}
        )

    # Try to serve the file if it exists
    file_path = frontend_dist / full_path
    if file_path.is_file():
        return FileResponse(file_path)

    # Otherwise serve index.html for SPA routing
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return JSONResponse(status_code=404, content={"error": "Frontend not built"})


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404, content={"error": "Not found", "path": request.url.path}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=WEB_HOST,
        port=WEB_PORT,
        reload=WEB_VERBOSE_LOGGING,
        log_level="debug" if WEB_VERBOSE_LOGGING else "info",
    )
