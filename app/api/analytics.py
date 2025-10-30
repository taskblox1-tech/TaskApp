"""
Analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile
from app.models.task_completion import TaskCompletion
from datetime import date, datetime, timedelta
from typing import Optional

router = APIRouter()


@router.get("/child/{child_id}")
async def get_child_analytics(
    child_id: int,
    period: str = Query("week", regex="^(day|week|month|year|all)$"),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific child
    Period options: day, week, month, year, all
    """
    # Verify parent has access to this child
    child = db.query(Profile).filter(
        Profile.id == child_id,
        Profile.family_id == current_user.family_id
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    # Calculate date range based on period
    today = date.today()
    if period == "day":
        start_date = today
        end_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())  # Monday
        end_date = today
    elif period == "month":
        start_date = date(today.year, today.month, 1)
        end_date = today
    elif period == "year":
        start_date = date(today.year, 1, 1)
        end_date = today
    else:  # all
        start_date = date(2020, 1, 1)  # Far past date
        end_date = today

    # Get all completions in date range
    completions = db.query(TaskCompletion).filter(
        TaskCompletion.child_id == child_id,
        TaskCompletion.completion_date >= start_date,
        TaskCompletion.completion_date <= end_date
    ).all()

    # Calculate overall stats
    total_tasks = len(completions)
    total_points = sum(c.points_earned for c in completions)

    # Group by period (morning/evening/anytime)
    by_period = {}
    for completion in completions:
        period_key = completion.task_period
        if period_key not in by_period:
            by_period[period_key] = {"tasks": 0, "points": 0}
        by_period[period_key]["tasks"] += 1
        by_period[period_key]["points"] += completion.points_earned

    # Group by category
    by_category = {}
    for completion in completions:
        category_key = completion.task_category
        if category_key not in by_category:
            by_category[category_key] = {"tasks": 0, "points": 0}
        by_category[category_key]["tasks"] += 1
        by_category[category_key]["points"] += completion.points_earned

    # Get daily breakdown for charts
    daily_stats = db.query(
        TaskCompletion.completion_date,
        func.count(TaskCompletion.id).label('task_count'),
        func.sum(TaskCompletion.points_earned).label('points_total')
    ).filter(
        TaskCompletion.child_id == child_id,
        TaskCompletion.completion_date >= start_date,
        TaskCompletion.completion_date <= end_date
    ).group_by(TaskCompletion.completion_date).order_by(TaskCompletion.completion_date).all()

    daily_breakdown = [
        {
            "date": str(stat.completion_date),
            "tasks": stat.task_count,
            "points": stat.points_total or 0
        }
        for stat in daily_stats
    ]

    # Calculate averages
    num_days = (end_date - start_date).days + 1
    avg_tasks_per_day = total_tasks / num_days if num_days > 0 else 0
    avg_points_per_day = total_points / num_days if num_days > 0 else 0

    # Find best day
    best_day = max(daily_breakdown, key=lambda x: x['points']) if daily_breakdown else None

    return {
        "child_id": child_id,
        "child_name": f"{child.first_name} {child.last_name}",
        "period": period,
        "date_range": {
            "start": str(start_date),
            "end": str(end_date),
            "days": num_days
        },
        "overall": {
            "total_tasks": total_tasks,
            "total_points": total_points,
            "avg_tasks_per_day": round(avg_tasks_per_day, 2),
            "avg_points_per_day": round(avg_points_per_day, 2),
            "current_streak": child.current_streak,
            "longest_streak": child.longest_streak
        },
        "by_period": by_period,
        "by_category": by_category,
        "daily_breakdown": daily_breakdown,
        "best_day": best_day
    }


@router.get("/family")
async def get_family_analytics(
    period: str = Query("week", regex="^(day|week|month|year|all)$"),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated analytics for entire family
    """
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="No family found")

    # Calculate date range
    today = date.today()
    if period == "day":
        start_date = today
        end_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif period == "month":
        start_date = date(today.year, today.month, 1)
        end_date = today
    elif period == "year":
        start_date = date(today.year, 1, 1)
        end_date = today
    else:  # all
        start_date = date(2020, 1, 1)
        end_date = today

    # Get all family completions
    completions = db.query(TaskCompletion).filter(
        TaskCompletion.family_id == current_user.family_id,
        TaskCompletion.completion_date >= start_date,
        TaskCompletion.completion_date <= end_date
    ).all()

    # Overall family stats
    total_tasks = len(completions)
    total_points = sum(c.points_earned for c in completions)

    # Group by child
    by_child = {}
    for completion in completions:
        child_id = completion.child_id
        if child_id not in by_child:
            child = completion.child
            by_child[child_id] = {
                "child_name": f"{child.first_name} {child.last_name}",
                "tasks": 0,
                "points": 0
            }
        by_child[child_id]["tasks"] += 1
        by_child[child_id]["points"] += completion.points_earned

    # Group by category
    by_category = {}
    for completion in completions:
        category_key = completion.task_category
        if category_key not in by_category:
            by_category[category_key] = {"tasks": 0, "points": 0}
        by_category[category_key]["tasks"] += 1
        by_category[category_key]["points"] += completion.points_earned

    # Group by period
    by_period = {}
    for completion in completions:
        period_key = completion.task_period
        if period_key not in by_period:
            by_period[period_key] = {"tasks": 0, "points": 0}
        by_period[period_key]["tasks"] += 1
        by_period[period_key]["points"] += completion.points_earned

    # Get all children in family
    children = db.query(Profile).filter(
        Profile.family_id == current_user.family_id,
        Profile.role == "child"
    ).all()

    children_summary = [
        {
            "id": child.id,
            "name": f"{child.first_name} {child.last_name}",
            "tasks": by_child.get(child.id, {}).get("tasks", 0),
            "points": by_child.get(child.id, {}).get("points", 0),
            "current_streak": child.current_streak,
            "longest_streak": child.longest_streak
        }
        for child in children
    ]

    num_days = (end_date - start_date).days + 1

    return {
        "family_id": current_user.family_id,
        "period": period,
        "date_range": {
            "start": str(start_date),
            "end": str(end_date),
            "days": num_days
        },
        "overall": {
            "total_tasks": total_tasks,
            "total_points": total_points,
            "avg_tasks_per_day": round(total_tasks / num_days, 2) if num_days > 0 else 0,
            "avg_points_per_day": round(total_points / num_days, 2) if num_days > 0 else 0
        },
        "by_child": children_summary,
        "by_category": by_category,
        "by_period": by_period
    }


@router.get("/trends/{child_id}")
async def get_child_trends(
    child_id: int,
    days: int = Query(30, ge=7, le=365),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get trend data for charts (last N days)
    """
    # Verify access
    child = db.query(Profile).filter(
        Profile.id == child_id,
        Profile.family_id == current_user.family_id
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # Get daily stats
    daily_stats = db.query(
        TaskCompletion.completion_date,
        func.count(TaskCompletion.id).label('task_count'),
        func.sum(TaskCompletion.points_earned).label('points_total')
    ).filter(
        TaskCompletion.child_id == child_id,
        TaskCompletion.completion_date >= start_date,
        TaskCompletion.completion_date <= end_date
    ).group_by(TaskCompletion.completion_date).order_by(TaskCompletion.completion_date).all()

    # Fill in missing days with zeros
    date_dict = {stat.completion_date: {"tasks": stat.task_count, "points": stat.points_total or 0} for stat in daily_stats}

    trend_data = []
    current_date = start_date
    while current_date <= end_date:
        if current_date in date_dict:
            trend_data.append({
                "date": str(current_date),
                "tasks": date_dict[current_date]["tasks"],
                "points": date_dict[current_date]["points"]
            })
        else:
            trend_data.append({
                "date": str(current_date),
                "tasks": 0,
                "points": 0
            })
        current_date += timedelta(days=1)

    return {
        "child_id": child_id,
        "child_name": f"{child.first_name} {child.last_name}",
        "days": days,
        "trend_data": trend_data
    }
