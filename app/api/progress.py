# ============= app/api/progress.py =============
"""
Progress API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile
from app.models.daily_progress import DailyProgress
from datetime import date

router = APIRouter()

@router.get("/daily")
async def get_daily_progress(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily progress for current user"""
    today = date.today()
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date == today
    ).all()
    
    return {
        "progress": {
            "date": today.isoformat(),
            "completed_count": len(progress),
            "total_points": sum(p.points_earned for p in progress),
            "tasks": [
                {
                    "task_id": p.task_id,
                    "task_title": p.task.title if p.task else "Unknown",
                    "points_earned": p.points_earned,
                    "completed": p.completed
                }
                for p in progress
            ]
        }
    }

@router.get("/daily")
async def get_daily_progress(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily progress"""
    return {"progress": {}}