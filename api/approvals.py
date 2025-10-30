# ==============================================================================
# FILE: app/api/approvals.py
# Task approval endpoints
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.profile import Profile
from app.models.task_approval import TaskApproval, ApprovalStatus
from app.models.daily_progress import DailyProgress
from app.models.task import Task
from app.core.dependencies import require_parent

router = APIRouter()


@router.get("/pending")
async def get_pending_approvals(
    current_user: Profile = Depends(require_parent),
    db: Session = Depends(get_db)
):
    """Get all pending approval requests for family"""
    
    approvals = db.query(TaskApproval).filter(
        TaskApproval.status == ApprovalStatus.PENDING
    ).join(Profile, TaskApproval.child_id == Profile.id).filter(
        Profile.family_id == current_user.family_id
    ).all()
    
    result = []
    for approval in approvals:
        child = db.query(Profile).filter(Profile.id == approval.child_id).first()
        task = db.query(Task).filter(Task.id == approval.task_id).first()
        
        result.append({
            "id": approval.id,
            "task": {
                "id": task.id,
                "title": task.title,
                "icon": task.icon,
                "points": task.points
            },
            "child": {
                "id": child.id,
                "first_name": child.first_name,
                "theme": child.theme
            },
            "date_for": approval.date_for.isoformat(),
            "proof_text": approval.proof_text,
            "requested_at": approval.requested_at.isoformat()
        })
    
    return result


@router.post("/{approval_id}/approve")
async def approve_request(
    approval_id: int,
    notes: dict,
    current_user: Profile = Depends(require_parent),
    db: Session = Depends(get_db)
):
    """Approve a task completion request"""
    
    approval = db.query(TaskApproval).filter(TaskApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    # Verify child is in same family
    child = db.query(Profile).filter(Profile.id == approval.child_id).first()
    if child.family_id != current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Get task
    task = db.query(Task).filter(Task.id == approval.task_id).first()
    
    # Update approval
    approval.status = ApprovalStatus.APPROVED
    approval.approved_by = current_user.id
    approval.approved_at = datetime.utcnow()
    approval.notes = notes.get("notes", "")
    
    # Get or create progress for that date
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == approval.child_id,
        DailyProgress.date == approval.date_for
    ).first()
    
    if not progress:
        progress = DailyProgress(
            child_id=approval.child_id,
            date=approval.date_for,
            total_points=0,
            completed_task_ids=[],
            pending_approval_ids=[]
        )
        db.add(progress)
        db.flush()
    
    # Move from pending to completed
    pending_ids = progress.pending_approval_ids or []
    completed_ids = progress.completed_task_ids or []
    
    if approval.task_id in pending_ids:
        pending_ids.remove(approval.task_id)
    completed_ids.append(approval.task_id)
    
    progress.pending_approval_ids = pending_ids
    progress.completed_task_ids = completed_ids
    progress.total_points += task.points
    
    # Update lifetime points
    child.total_lifetime_points += task.points
    
    db.commit()
    
    return {
        "message": "Task approved!",
        "points_awarded": task.points
    }


@router.post("/{approval_id}/deny")
async def deny_request(
    approval_id: int,
    notes: dict,
    current_user: Profile = Depends(require_parent),
    db: Session = Depends(get_db)
):
    """Deny a task completion request"""
    
    approval = db.query(TaskApproval).filter(TaskApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    # Verify child is in same family
    child = db.query(Profile).filter(Profile.id == approval.child_id).first()
    if child.family_id != current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Update approval
    approval.status = ApprovalStatus.DENIED
    approval.approved_by = current_user.id
    approval.approved_at = datetime.utcnow()
    approval.notes = notes.get("notes", "")
    
    # Remove from pending list
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == approval.child_id,
        DailyProgress.date == approval.date_for
    ).first()
    
    if progress:
        pending_ids = progress.pending_approval_ids or []
        if approval.task_id in pending_ids:
            pending_ids.remove(approval.task_id)
        progress.pending_approval_ids = pending_ids
    
    db.commit()
    
    return {"message": "Request denied"}


# ==============================================================================
# FILE: app/api/progress.py
# Progress tracking endpoints
# ==============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database import get_db
from app.models.profile import Profile
from app.models.daily_progress import DailyProgress
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/today")
async def get_today_progress(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's progress for current user"""
    
    today = date.today()
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date == today
    ).first()
    
    if not progress:
        return {
            "date": today.isoformat(),
            "total_points": 0,
            "completed_tasks": 0,
            "pending_tasks": 0
        }
    
    return {
        "date": progress.date.isoformat(),
        "total_points": progress.total_points,
        "completed_tasks": len(progress.completed_task_ids or []),
        "pending_tasks": len(progress.pending_approval_ids or [])
    }


@router.get("/weekly")
async def get_weekly_progress(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get this week's progress"""
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    progress_records = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date >= week_start,
        DailyProgress.date <= week_end
    ).all()
    
    total_points = sum(p.total_points for p in progress_records)
    total_tasks = sum(len(p.completed_task_ids or []) for p in progress_records)
    
    daily_breakdown = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_progress = next((p for p in progress_records if p.date == day), None)
        daily_breakdown.append({
            "date": day.isoformat(),
            "day_name": day.strftime("%A"),
            "points": day_progress.total_points if day_progress else 0,
            "tasks": len(day_progress.completed_task_ids or []) if day_progress else 0
        })
    
    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "total_points": total_points,
        "total_tasks": total_tasks,
        "daily": daily_breakdown
    }


# ==============================================================================
# FILE: app/api/families.py
# Family management endpoints
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.profile import Profile, UserRole
from app.models.family import Family
from app.core.dependencies import get_current_user, require_admin

router = APIRouter()


@router.get("/mine")
async def get_my_family(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's family information"""
    
    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    members = db.query(Profile).filter(Profile.family_id == family.id).all()
    
    return {
        "id": family.id,
        "name": family.name,
        "join_code": family.join_code if current_user.role in [UserRole.ADMIN, UserRole.PARENT] else None,
        "members": [
            {
                "id": m.id,
                "first_name": m.first_name,
                "last_name": m.last_name,
                "role": m.role.value,
                "theme": m.theme,
                "total_lifetime_points": m.total_lifetime_points
            }
            for m in members
        ]
    }


@router.get("/members")
async def get_family_members(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all family members"""
    
    members = db.query(Profile).filter(
        Profile.family_id == current_user.family_id
    ).all()
    
    return [
        {
            "id": m.id,
            "first_name": m.first_name,
            "last_name": m.last_name,
            "role": m.role.value,
            "theme": m.theme,
            "total_lifetime_points": m.total_lifetime_points
        }
        for m in members
    ]


# ==============================================================================
# FILE: app/api/rewards.py
# Rewards management endpoints
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.profile import Profile
from app.models.reward import Reward, RewardType
from app.models.daily_progress import DailyProgress
from app.core.dependencies import get_current_user, require_parent

router = APIRouter()


@router.get("/")
async def get_rewards(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active rewards for family"""
    
    rewards = db.query(Reward).filter(
        Reward.family_id == current_user.family_id,
        Reward.is_active == 1
    ).all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "cost": r.cost,
            "icon": r.icon,
            "type": r.type.value
        }
        for r in rewards
    ]


@router.post("/")
async def create_reward(
    reward_data: dict,
    current_user: Profile = Depends(require_parent),
    db: Session = Depends(get_db)
):
    """Create a new reward (parent/admin only)"""
    
    type_map = {
        "screen_time": RewardType.SCREEN_TIME,
        "treat": RewardType.TREAT,
        "activity": RewardType.ACTIVITY,
        "allowance": RewardType.ALLOWANCE,
        "special": RewardType.SPECIAL,
        "privilege": RewardType.PRIVILEGE
    }
    
    new_reward = Reward(
        family_id=current_user.family_id,
        name=reward_data["name"],
        description=reward_data.get("description"),
        cost=reward_data["cost"],
        icon=reward_data.get("icon", "🎁"),
        type=type_map.get(reward_data.get("type", "special"), RewardType.SPECIAL)
    )
    
    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)
    
    return {"id": new_reward.id, "message": "Reward created successfully"}


@router.post("/{reward_id}/redeem")
async def redeem_reward(
    reward_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redeem a reward with points"""
    
    reward = db.query(Reward).filter(
        Reward.id == reward_id,
        Reward.family_id == current_user.family_id
    ).first()
    
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    # Get today's progress
    today = date.today()
    progress = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.date == today
    ).first()
    
    if not progress or progress.total_points < reward.cost:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough points. Need {reward.cost}, have {progress.total_points if progress else 0}"
        )
    
    # Deduct points
    progress.total_points -= reward.cost
    
    # Add to redeemed list
    redeemed_ids = progress.redeemed_reward_ids or []
    redeemed_ids.append(reward_id)
    progress.redeemed_reward_ids = redeemed_ids
    
    db.commit()
    
    return {
        "message": f"Redeemed {reward.name}!",
        "points_spent": reward.cost,
        "remaining_points": progress.total_points
    }