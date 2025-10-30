"""
Tasks API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.daily_progress import DailyProgress
from datetime import date, timedelta

router = APIRouter()


def update_streak(user: Profile, db: Session):
    """Update user's streak when they complete tasks"""
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Check if there's activity yesterday
    yesterday_progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == user.id,
        DailyProgress.date == yesterday
    ).first()

    # Check if there's activity for any day before today
    last_activity = db.query(DailyProgress).filter(
        DailyProgress.child_id == user.id,
        DailyProgress.date < today
    ).order_by(DailyProgress.date.desc()).first()

    if yesterday_progress and len(yesterday_progress.completed_task_ids or []) > 0:
        # Consecutive day - increment streak
        user.current_streak += 1
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
    elif last_activity:
        # There was activity before but not yesterday - reset streak to 1
        user.current_streak = 1
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
    else:
        # First ever activity - start streak
        user.current_streak = 1
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak

    return user.current_streak


@router.get("/")
@router.get("/my-tasks")
async def get_my_tasks(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to current child"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Tasks endpoint called. Current user: {current_user}")
    if current_user:
        logger.info(f"User ID: {current_user.id}, Family ID: {current_user.family_id}, Role: {current_user.role}")

    if not current_user or not current_user.family_id:
        logger.warning("No current user or family_id, returning empty tasks")
        return {"tasks": []}
    
    # If child, return only assigned tasks
    if current_user.role == "child":
        logger.info(f"Child user detected, fetching task assignments for child_id={current_user.id}")
        assignments = db.query(TaskAssignment).filter(
            TaskAssignment.child_id == current_user.id
        ).all()
        logger.info(f"Found {len(assignments)} task assignments")

        task_ids = [a.task_id for a in assignments]
        logger.info(f"Task IDs: {task_ids}")
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).all() if task_ids else []
        logger.info(f"Found {len(tasks)} tasks")
    else:
        # If parent, return all family tasks
        tasks = db.query(Task).filter(Task.family_id == current_user.family_id).all()
    
    return {
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "icon": task.icon or "✅",
                "points": task.points,
                "period": str(task.period.value) if hasattr(task.period, 'value') else str(task.period),
                "category": str(task.category.value) if hasattr(task.category, 'value') else str(task.category),
                "day_type": str(task.day_type.value) if hasattr(task.day_type, 'value') else str(task.day_type),
                "requires_approval": bool(task.requires_approval)
            }
            for task in tasks
        ]
    }


@router.post("/")
async def create_task(
    task_data: dict,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task (parent only)"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can create tasks")

    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="No family found")

    # Create the task
    from app.models.task import TaskPeriod, TaskCategory, TaskDayType

    new_task = Task(
        family_id=current_user.family_id,
        title=task_data.get("title"),
        description=task_data.get("description", ""),
        points=task_data.get("points", 10),
        icon=task_data.get("icon", "✅"),
        period=TaskPeriod(task_data.get("period", "anytime")),
        category=TaskCategory.CHORES,  # Default category
        day_type=TaskDayType(task_data.get("day_type", "anyday")),
        requires_approval=1 if task_data.get("requires_approval", False) else 0,
        library_category=task_data.get("library_category", ""),
        is_active=1
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Optionally assign to specific children
    assigned_child_ids = task_data.get("assigned_to", [])
    if assigned_child_ids:
        for child_id in assigned_child_ids:
            assignment = TaskAssignment(
                task_id=new_task.id,
                child_id=child_id
            )
            db.add(assignment)
        db.commit()

    return {
        "id": new_task.id,
        "title": new_task.title,
        "message": "Task created successfully!"
    }


@router.post("/{task_id}/complete")
async def complete_task(
    task_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a task as complete"""
    from app.models.task_approval import TaskApproval, ApprovalStatus
    from sqlalchemy.orm.attributes import flag_modified

    # Verify task exists and belongs to family
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.family_id == current_user.family_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get or create today's progress record
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
            pending_approval_ids=[],
            redeemed_reward_ids=[]
        )
        db.add(progress)

    # Check if already completed or pending
    if task_id in (progress.completed_task_ids or []):
        raise HTTPException(status_code=400, detail="Task already completed today")
    if task_id in (progress.pending_approval_ids or []):
        raise HTTPException(status_code=400, detail="Task pending approval")

    # Check if task requires approval
    if task.requires_approval:
        # Add to pending approvals list
        if progress.pending_approval_ids is None:
            progress.pending_approval_ids = []
        progress.pending_approval_ids.append(task_id)
        flag_modified(progress, 'pending_approval_ids')

        # Create approval request
        approval = TaskApproval(
            task_id=task_id,
            child_id=current_user.id,
            date_for=today,
            status=ApprovalStatus.PENDING
        )
        db.add(approval)
        db.commit()

        return {"message": "Task submitted for approval!", "requires_approval": True}
    else:
        # Add to completed tasks and award points immediately
        if progress.completed_task_ids is None:
            progress.completed_task_ids = []
        progress.completed_task_ids.append(task_id)
        progress.total_points += task.points
        flag_modified(progress, 'completed_task_ids')

        # Update user's total points
        current_user.total_lifetime_points += task.points

        # Update streak
        streak_count = update_streak(current_user, db)

        db.commit()

        return {
            "message": "Task completed!",
            "points_earned": task.points,
            "new_total": current_user.total_lifetime_points,
            "current_streak": streak_count
        }


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: dict,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task (parent only)"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can update tasks")

    # Verify task exists and belongs to family
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.family_id == current_user.family_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task fields
    from app.models.task import TaskPeriod, TaskDayType

    if "title" in task_data:
        task.title = task_data["title"]
    if "description" in task_data:
        task.description = task_data["description"]
    if "icon" in task_data:
        task.icon = task_data["icon"]
    if "points" in task_data:
        task.points = task_data["points"]
    if "period" in task_data:
        task.period = TaskPeriod(task_data["period"])
    if "day_type" in task_data:
        task.day_type = TaskDayType(task_data["day_type"])
    if "requires_approval" in task_data:
        task.requires_approval = 1 if task_data["requires_approval"] else 0

    # Update assignments if provided
    if "assigned_to" in task_data:
        # Delete existing assignments
        db.query(TaskAssignment).filter(TaskAssignment.task_id == task_id).delete()

        # Add new assignments
        for child_id in task_data["assigned_to"]:
            assignment = TaskAssignment(
                task_id=task_id,
                child_id=child_id
            )
            db.add(assignment)

    db.commit()
    return {"message": "Task updated successfully!"}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task (parent only)"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can delete tasks")

    # Verify task exists and belongs to family
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.family_id == current_user.family_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete task assignments first (foreign key constraint)
    db.query(TaskAssignment).filter(TaskAssignment.task_id == task_id).delete()

    # Delete the task
    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully!"}


@router.get("/{task_id}/assignments")
async def get_task_assignments(
    task_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get children assigned to a task"""
    # Verify task exists and belongs to family
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.family_id == current_user.family_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    assignments = db.query(TaskAssignment).filter(
        TaskAssignment.task_id == task_id
    ).all()

    return {"assigned_child_ids": [a.child_id for a in assignments]}