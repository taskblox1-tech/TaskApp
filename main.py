# ==============================================================================
# FILE: main.py
# Main FastAPI application with all routes and configuration
# ==============================================================================

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from app.config import get_settings
from app.database import get_db, init_db
from app.core.dependencies import get_current_user as get_current_user_from_cookie

# Import all models to ensure they're registered with SQLAlchemy
from app.models import (
    Family, Profile, Task, TaskAssignment,
    TaskApproval, DailyProgress, Reward
)

# Import API routers
from app.api import auth, tasks, approvals, progress, families, rewards

# Get settings instance
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Family Task Tracker with themes, approval workflow, and rewards",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# CORS Middleware
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
# Auto-reload templates in development only
if settings.DEBUG:
    templates.env.auto_reload = True
    templates.env.cache = None

# Add custom template filters
def format_points(value):
    """Format points with commas"""
    return f"{value:,}"

def get_emoji(theme_name, emoji_type="point"):
    """Get theme-specific emoji"""
    theme_emojis = {
        "minecraft": {"point": "⛏️", "success": "💎"},
        "roblox": {"point": "💎", "success": "🏆"},
        "barbie": {"point": "💎", "success": "✨"},
        "pokemon": {"point": "⭐", "success": "⚡"},
        "sports": {"point": "⚽", "success": "🏆"},
        "ninja_turtles": {"point": "🥷", "success": "🍕"},
    }
    return theme_emojis.get(theme_name, {}).get(emoji_type, "⭐")

templates.env.filters["format_points"] = format_points
templates.env.filters["get_emoji"] = get_emoji

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(families.router, prefix="/api/families", tags=["Families"])
app.include_router(rewards.router, prefix="/api/rewards", tags=["Rewards"])


# ==============================================================================
# STARTUP & SHUTDOWN EVENTS
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down application")


# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Endpoint not found"}
        )
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors"""
    logger.error(f"Internal error: {exc}")
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=500
    )


# ==============================================================================
# PUBLIC ROUTES (No authentication required)
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie)
):
    """Home page - redirect based on auth status"""
    if current_user:
        # Redirect based on role
        if current_user.role.value == "child":
            return RedirectResponse(url="/child/dashboard", status_code=302)
        else:
            return RedirectResponse(url="/parent/dashboard", status_code=302)
    
    return RedirectResponse(url="/auth/login", status_code=302)


@app.get("/auth/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie)
):
    """Login page"""
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


@app.get("/auth/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie)
):
    """Registration page"""
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )


@app.get("/auth/logout")
async def logout():
    """Logout - clear cookie and redirect"""
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# ==============================================================================
# PARENT/ADMIN ROUTES
# ==============================================================================

@app.get("/parent/dashboard", response_class=HTMLResponse)
async def parent_dashboard(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Parent dashboard"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    if current_user.role.value not in ["admin", "parent"]:
        return RedirectResponse(url="/child/dashboard", status_code=302)
    
    # Get family members
    from app.models.profile import Profile as ProfileModel
    children = db.query(ProfileModel).filter(
        ProfileModel.family_id == current_user.family_id,
        ProfileModel.role == "child"
    ).all()
    
    # Get pending approvals count
    from app.models.task_approval import TaskApproval, ApprovalStatus
    pending_count = db.query(TaskApproval).filter(
        TaskApproval.status == ApprovalStatus.PENDING
    ).join(ProfileModel, TaskApproval.child_id == ProfileModel.id).filter(
        ProfileModel.family_id == current_user.family_id
    ).count()
    
    return templates.TemplateResponse(
        "parent/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "children": children,
            "pending_approvals": pending_count
        }
    )


@app.get("/parent/task-library", response_class=HTMLResponse)
async def task_library(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Browse and add tasks from library"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    if current_user.role.value not in ["admin", "parent"]:
        return RedirectResponse(url="/", status_code=302)
    
    # Get existing tasks
    from app.models.task import Task
    existing_tasks = db.query(Task).filter(
        Task.family_id == current_user.family_id,
        Task.is_active == 1
    ).all()
    
    # Get children for assignment
    from app.models.profile import Profile as ProfileModel
    children = db.query(ProfileModel).filter(
        ProfileModel.family_id == current_user.family_id,
        ProfileModel.role == "child"
    ).all()
    
    return templates.TemplateResponse(
        "parent/task-library.html",
        {
            "request": request,
            "user": current_user,
            "existing_tasks": existing_tasks,
            "children": children
        }
    )


@app.get("/parent/approval-queue", response_class=HTMLResponse)
async def approval_queue(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """View pending approval requests"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    if current_user.role.value not in ["admin", "parent"]:
        return RedirectResponse(url="/", status_code=302)
    
    # Get pending approvals
    from app.models.task_approval import TaskApproval, ApprovalStatus
    from app.models.task import Task
    from app.models.profile import Profile as ProfileModel
    
    pending_approvals = db.query(TaskApproval).filter(
        TaskApproval.status == ApprovalStatus.PENDING
    ).join(ProfileModel, TaskApproval.child_id == ProfileModel.id).filter(
        ProfileModel.family_id == current_user.family_id
    ).all()
    
    return templates.TemplateResponse(
        "parent/approval-queue.html",
        {
            "request": request,
            "user": current_user,
            "pending_approvals": pending_approvals
        }
    )


# ==============================================================================
# CHILD ROUTES
# ==============================================================================

@app.get("/child/dashboard", response_class=HTMLResponse)
async def child_dashboard(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Child dashboard with tasks"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Get today's progress
    from datetime import date
    from app.models.daily_progress import DailyProgress
    from app.models.task import Task
    from app.models.task_assignment import TaskAssignment
    
    today = date.today()
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date == today
    ).first()
    
    if not progress:
        progress = DailyProgress(
            child_id=current_user.id,
            date=today,
            total_points=0,
            completed_task_ids=[],
            pending_approval_ids=[]
        )
        db.add(progress)
        db.commit()
    
    # Get assigned tasks
    assigned_tasks = db.query(Task).join(TaskAssignment).filter(
        TaskAssignment.child_id == current_user.id,
        Task.is_active == 1
    ).all()
    
    # Organize tasks by period
    morning_tasks = [t for t in assigned_tasks if t.period.value == "morning"]
    evening_tasks = [t for t in assigned_tasks if t.period.value == "evening"]
    anytime_tasks = [t for t in assigned_tasks if t.period.value == "anytime"]
    
    return templates.TemplateResponse(
        "child/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "progress": progress,
            "morning_tasks": morning_tasks,
            "evening_tasks": evening_tasks,
            "anytime_tasks": anytime_tasks,
            "completed_ids": progress.completed_task_ids or [],
            "pending_ids": progress.pending_approval_ids or []
        }
    )


@app.get("/child/rewards", response_class=HTMLResponse)
async def child_rewards(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """View rewards catalog"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Get available rewards
    from app.models.reward import Reward
    from datetime import date
    from app.models.daily_progress import DailyProgress
    
    rewards = db.query(Reward).filter(
        Reward.family_id == current_user.family_id,
        Reward.is_active == 1
    ).all()
    
    # Get today's points
    today = date.today()
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date == today
    ).first()
    
    current_points = progress.total_points if progress else 0
    
    return templates.TemplateResponse(
        "child/rewards.html",
        {
            "request": request,
            "user": current_user,
            "rewards": rewards,
            "current_points": current_points
        }
    )


@app.get("/child/profile", response_class=HTMLResponse)
async def child_profile(
    request: Request,
    current_user: Profile = Depends(get_current_user_from_cookie)
):
    """Child profile and theme settings"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "child/profile.html",
        {
            "request": request,
            "user": current_user
        }
    )


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}


# ==============================================================================
# RUN APPLICATION
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )