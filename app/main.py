"""
Family Task Tracker - Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.database import engine, Base

# Import all models to ensure they're registered
from app.models import (
    Family, Profile, Task, TaskAssignment, 
    TaskApproval, DailyProgress, Reward
)

# Import API routers
from app.api import auth, tasks, approvals, progress, families, rewards

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Family Task Tracker",
    description="Gamified task management for families",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(families.router, prefix="/api/families", tags=["families"])
app.include_router(rewards.router, prefix="/api/rewards", tags=["rewards"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting Family Task Tracker...")
    logger.info(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'SQLite'}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Home page - redirects to login"""
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("auth/register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard - role-based redirect handled by frontend"""
    return templates.TemplateResponse("child/dashboard.html", {"request": request})


@app.get("/parent/dashboard", response_class=HTMLResponse)
async def parent_dashboard(request: Request):
    """Parent dashboard"""
    return templates.TemplateResponse("parent/dashboard.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )