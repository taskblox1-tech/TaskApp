# ============= app/api/progress.py =============
"""
Progress API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile
from app.models.daily_progress import DailyProgress
from datetime import date, datetime, timedelta

router = APIRouter()


@router.get("/stats")
async def get_progress_stats(
    period: str = Query("today", regex="^(today|week|month|year|all)$"),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress statistics for different time periods"""

    today = date.today()

    # Calculate date range based on period
    if period == "today":
        start_date = today
        end_date = today
    elif period == "week":
        # Current week (Monday to Sunday)
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        # Current month
        start_date = today.replace(day=1)
        # Last day of current month
        if today.month == 12:
            end_date = today.replace(month=12, day=31)
        else:
            end_date = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
    elif period == "year":
        # Current year
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:  # "all"
        # All time - get earliest record
        earliest = db.query(func.min(DailyProgress.date)).filter(
            DailyProgress.child_id == current_user.id
        ).scalar()
        start_date = earliest if earliest else today
        end_date = today

    # Query progress records in date range
    progress_records = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date >= start_date,
        DailyProgress.date <= end_date
    ).all()

    # Calculate statistics
    total_points = sum(p.total_points or 0 for p in progress_records)
    total_completed = sum(len(p.completed_task_ids or []) for p in progress_records)
    days_active = len(progress_records)

    # Calculate average daily points (only for active days)
    avg_daily_points = total_points / days_active if days_active > 0 else 0

    # Find best day
    best_day = None
    best_day_points = 0
    for p in progress_records:
        if (p.total_points or 0) > best_day_points:
            best_day_points = p.total_points or 0
            best_day = p.date.isoformat()

    # Calculate streak (consecutive days with activity)
    current_streak = 0
    check_date = today
    while True:
        has_activity = any(p.date == check_date for p in progress_records)
        if has_activity:
            current_streak += 1
            check_date = check_date - timedelta(days=1)
        else:
            break

    # Get today's completed and pending tasks for display
    today_progress = next((p for p in progress_records if p.date == today), None)
    completed_task_ids = today_progress.completed_task_ids if today_progress else []
    pending_approval_ids = today_progress.pending_approval_ids if today_progress else []

    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_points": total_points,
        "total_completed": total_completed,
        "days_active": days_active,
        "avg_daily_points": round(avg_daily_points, 1),
        "best_day": best_day,
        "best_day_points": best_day_points,
        "current_streak": current_streak,
        "completed_task_ids": completed_task_ids or [],
        "pending_approval_ids": pending_approval_ids or []
    }


@router.get("/history")
async def get_progress_history(
    days: int = Query(7, ge=1, le=365),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily progress history for charts"""

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    progress_records = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date >= start_date,
        DailyProgress.date <= end_date
    ).order_by(DailyProgress.date).all()

    # Create a complete date range
    history = []
    current_date = start_date
    while current_date <= end_date:
        progress = next((p for p in progress_records if p.date == current_date), None)
        history.append({
            "date": current_date.isoformat(),
            "points": progress.total_points if progress else 0,
            "tasks_completed": len(progress.completed_task_ids) if progress and progress.completed_task_ids else 0
        })
        current_date += timedelta(days=1)

    return {"history": history}
