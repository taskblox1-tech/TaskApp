"""
Approvals API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile
from app.models.task_approval import TaskApproval, ApprovalStatus
from app.models.task import Task

router = APIRouter()

@router.get("/")
async def get_approvals(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending approval requests"""
    if not current_user or not current_user.family_id:
        return {"approvals": []}

    # Query approvals with eager loading of relationships
    approvals = db.query(TaskApproval).options(
        joinedload(TaskApproval.task),
        joinedload(TaskApproval.child)
    ).join(
        Task, TaskApproval.task_id == Task.id
    ).filter(
        TaskApproval.status == ApprovalStatus.PENDING,
        Task.family_id == current_user.family_id
    ).all()

    return {
        "approvals": [
            {
                "id": a.id,
                "task_id": a.task_id,
                "task_title": a.task.title if a.task else "Unknown",
                "task_icon": a.task.icon if a.task else "📋",
                "child_id": a.child_id,
                "child_name": f"{a.child.first_name} {a.child.last_name}" if a.child else "Unknown",
                "status": a.status.value,
                "created_at": a.requested_at.isoformat() if a.requested_at else ""
            }
            for a in approvals
        ]
    }


@router.post("/{approval_id}/approve")
async def approve_task(
    approval_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a task completion"""
    from app.models.daily_progress import DailyProgress

    if not current_user or not current_user.family_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    approval = db.query(TaskApproval).join(
        TaskApproval.task
    ).filter(
        TaskApproval.id == approval_id
    ).first()

    # Verify approval belongs to user's family
    if approval and approval.task and approval.task.family_id != current_user.family_id:
        approval = None

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    approval.status = ApprovalStatus.APPROVED
    approval.approved_by = current_user.id
    approval.approved_at = datetime.utcnow()

    # Award points to child and update progress
    if approval.child and approval.task:
        approval.child.total_lifetime_points += approval.task.points

        # Get or create daily progress entry
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
                pending_approval_ids=[],
                redeemed_reward_ids=[]
            )
            db.add(progress)

        # Move from pending to completed
        if progress.pending_approval_ids is None:
            progress.pending_approval_ids = []
        if approval.task_id in progress.pending_approval_ids:
            progress.pending_approval_ids.remove(approval.task_id)

        if progress.completed_task_ids is None:
            progress.completed_task_ids = []
        if approval.task_id not in progress.completed_task_ids:
            progress.completed_task_ids.append(approval.task_id)
            progress.total_points += approval.task.points

    db.commit()

    return {"message": "Task approved!"}


@router.post("/{approval_id}/deny")
async def deny_task(
    approval_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deny a task completion"""
    if not current_user or not current_user.family_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    approval = db.query(TaskApproval).join(
        TaskApproval.task
    ).filter(
        TaskApproval.id == approval_id
    ).first()

    # Verify approval belongs to user's family
    if approval and approval.task and approval.task.family_id != current_user.family_id:
        approval = None

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    approval.status = ApprovalStatus.DENIED
    approval.approved_by = current_user.id
    approval.approved_at = datetime.utcnow()

    db.commit()

    return {"message": "Task denied"}