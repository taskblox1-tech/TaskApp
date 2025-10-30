# ==============================================================================
# FILE: app/api/tasks.py
# Task management endpoints - CRUD operations and completion
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.profile import Profile, UserRole
from app.models.task import Task, TaskPeriod, TaskCategory, TaskDayType
from app.models.task_assignment import TaskAssignment
from app.models.daily_progress import DailyProgress
from app.models.task_approval import TaskApproval, ApprovalStatus
from app.core.dependencies import get_current_user, require_parent

router = APIRouter()


@router.get("/")
async def get_tasks(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active tasks for current user's family
    Children see only their assigned tasks
    Parents see all family tasks
    """
    
    if current_user.role == UserRole.CHILD:
        # Get only assigned tasks
        tasks = db.query(Task).join(TaskAssignment).filter(
            TaskAssignment.child_id == current_user.id,
            Task.is_active == 1
        ).all()
    else:
        # Get all family tasks
        tasks = db.query(Task).filter(
            Task.family_id == current_user.family_id,
            Task.is_active == 1
        ).all()
    
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "points": task.points,
            "icon": task.icon,
            "period": task.period.value,
            "category": task.category.value,
            "day_type": task.day_type.value,
            "requires_approval": bool(task.requires_approval),
            "library_category": task.library_category
        }
        for task in tasks
    ]


@router.post("/")
async def create_task(
    task_data: dict,
    current_user: Profile = Depends(require_parent),
    db: Session = Depends(get_db)
):
    """
    Create a new task (parent/admin only)
    """
    
    # Convert string enums to proper enum types
    period_map = {
        "morning": TaskPeriod.MORNING,
        "evening": TaskPeriod.EVENING,
        "anytime": TaskPeriod.ANYTIME
    }
    
    category_map = {
        "daily": TaskCategory.DAILY,
        "bonus": TaskCategory.BONUS,
        "general": TaskCategory.GENERAL,
        "academic": TaskCategory.ACADEMIC,
        "sports": TaskCategory.SPORTS,
        "creative": TaskCategory.CREATIVE,
        "chores": TaskCategory.CHORES,
        "health": TaskCategory.HEALTH
    }
    
    day_type_map = {
        "anyday": TaskDayType.ANYDAY,
        "weekday": TaskDayType.WEEKDAY,
        "weekend": TaskDayType.WEEKEND
    }
    
    new_task = Task(
        family_id=current_user.family_id,
        title=task_data["title"],
        description=task_data.get("description"),
        points=task_data["points"],
        icon=task_data.get("icon", "✅"),
        period=period_map.get(task_data.get("period", "anytime"), TaskPeriod.ANYTIME),
        category=category_map.get(task_data.get("category", "general"), TaskCategory.GENERAL),
        day_type=day_type_map.get(task_data.get("day_type", "anyday"), TaskDayType.ANYDAY),
        requires_approval=1 if task_data.get("requires_approval", False) else 0,
        library_category=task_data.get("library_category")
    )
    
    db.add(new_task)
    db.flush()
    
    # Assign to children if specified
    if "assign_to" in task_data and task_data["assign_to"]:
        for child_id in task_data["assign_to"]:
            assignment = TaskAssignment(
                task_id=new_task.id,
                child_id=child_id
            )
            db.add(assignment)
    
    db.commit()
    db.refresh(new_task)
    
    return {
        "id": new_task.id,
        "title": new_task.title,
        "points": new_task.points,
        "message": "Task created successfully"
    }


@router.patch("/{task_id}")
async def update_task(
    task_id: int,
    task_data: dict,
    current_user: Profile = Depends(require_parent),
    db: Session = Depends(get_db)
):
    """
    Update an existing task (parent/admin only)
    """
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.family_id == current_user.family_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields
    if "title" in task_data:
        task.title = task_data["title"]
    if "description" in task_data:
        task.description = task_data["description"]
    if "points" in task_data:
        task.points = task_data["points"]
    if "icon" in task_data:
        task.icon = task_data["icon"]
    if "requires_approval" in task_data:
        task.requires_approval = 1 if task_data["requires_approval"] else 0
    
    db.commit()
    db.refresh(task)
    
    return {"message": "Task updated successfully"}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: Profile = Depends(require_parent),
    db: Session = Depends(get_db)
):
    """
    Delete (deactivate) a task (parent/admin only)
    """
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.family_id == current_user.family_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Soft delete - just mark as inactive
    task.is_active = 0
    db.commit()
    
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/complete")
async def complete_task(
    task_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a task as complete
    If requires approval: Create approval request
    If no approval needed: Award points immediately
    """
    
    # Get task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify task is assigned to user
    assignment = db.query(TaskAssignment).filter(
        TaskAssignment.task_id == task_id,
        TaskAssignment.child_id == current_user.id
    ).first()
    
    if not assignment and current_user.role == UserRole.CHILD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task not assigned to you"
        )
    
    # Get or create today's progress
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
        db.flush()
    
    # Check if already completed today
    completed_ids = progress.completed_task_ids or []
    pending_ids = progress.pending_approval_ids or []
    
    if task_id in completed_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already completed today"
        )
    
    if task_id in pending_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already pending approval"
        )
    
    # Handle based on approval requirement
    if task.requires_approval:
        # Create approval request
        approval = TaskApproval(
            task_id=task_id,
            child_id=current_user.id,
            date_for=today,
            status=ApprovalStatus.PENDING
        )
        db.add(approval)
        
        # Add to pending list
        if not pending_ids:
            pending_ids = []
        pending_ids.append(task_id)
        progress.pending_approval_ids = pending_ids
        
        db.commit()
        
        return {
            "status": "pending_approval",
            "message": "Approval request sent to parent",
            "points": task.points
        }
    
    else:
        # Award points immediately
        if not completed_ids:
            completed_ids = []
        completed_ids.append(task_id)
        progress.completed_task_ids = completed_ids
        progress.total_points += task.points
        
        # Update lifetime points
        current_user.total_lifetime_points += task.points
        
        db.commit()
        
        return {
            "status": "completed",
            "message": f"Task completed! +{task.points} points",
            "points": task.points,
            "total_today": progress.total_points,
            "total_lifetime": current_user.total_lifetime_points
        }


@router.post("/{task_id}/uncomplete")
async def uncomplete_task(
    task_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Un-mark a task as complete (if no approval required)
    """
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Can't uncomplete tasks that require approval
    if task.requires_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot uncomplete tasks that require approval"
        )
    
    # Get today's progress
    today = date.today()
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date == today
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for today"
        )
    
    # Remove from completed list
    completed_ids = progress.completed_task_ids or []
    if task_id not in completed_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task was not completed"
        )
    
    completed_ids.remove(task_id)
    progress.completed_task_ids = completed_ids
    progress.total_points -= task.points
    
    # Update lifetime points
    current_user.total_lifetime_points = max(0, current_user.total_lifetime_points - task.points)
    
    db.commit()
    
    return {
        "message": "Task unmarked",
        "total_today": progress.total_points,
        "total_lifetime": current_user.total_lifetime_points
    }