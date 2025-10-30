"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.profile import Profile
from app.models.family import Family
from app.schemas.auth import UserLogin, UserRegister, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user
import hashlib

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    import string
    import random

    # Check if email already exists
    existing_user = db.query(Profile).filter(Profile.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Verify family if joining existing family
    family_id = None
    if user_data.join_code:
        family = db.query(Family).filter(Family.join_code == user_data.join_code).first()
        if not family:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid join code"
            )
        family_id = family.id
    elif user_data.family_id:
        family_id = user_data.family_id
    elif user_data.role == "parent":
        # Create new family for parent if no join code provided
        # Generate unique join code
        while True:
            join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            existing_family = db.query(Family).filter(Family.join_code == join_code).first()
            if not existing_family:
                break

        # Create family
        new_family = Family(
            name=f"{user_data.name}'s Family",
            join_code=join_code
        )
        db.add(new_family)
        db.flush()  # Get the family ID
        family_id = new_family.id

    # Parse name into first and last name
    name_parts = user_data.name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # Create new user
    new_user = Profile(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=first_name,
        last_name=last_name,
        role=user_data.role,
        family_id=family_id,
        theme="default" if user_data.role != "child" else "minecraft"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
        samesite="lax",
        path="/"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": f"{new_user.first_name} {new_user.last_name}",
            "role": new_user.role,
            "family_id": new_user.family_id,
            "theme": new_user.theme,
            "total_points": new_user.total_lifetime_points
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login user"""
    # Find user by email
    user = db.query(Profile).filter(Profile.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
        samesite="lax",
        path="/"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}",
            "role": user.role,
            "family_id": user.family_id,
            "theme": user.theme,
            "total_points": user.total_lifetime_points
        }
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Profile = Depends(get_current_user)):
    """Get current user info"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": f"{current_user.first_name} {current_user.last_name}",
        "role": current_user.role,
        "family_id": current_user.family_id,
        "theme": current_user.theme,
        "total_points": current_user.total_lifetime_points
    }


@router.get("/children")
async def get_children(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all children in current user's family"""
    if not current_user or not current_user.family_id:
        return {"children": []}

    children = db.query(Profile).filter(
        Profile.family_id == current_user.family_id,
        Profile.role == "child"
    ).all()

    return {
        "children": [
            {
                "id": child.id,
                "first_name": child.first_name,
                "last_name": child.last_name,
                "theme": child.theme,
                "total_lifetime_points": child.total_lifetime_points
            }
            for child in children
        ]
    }


@router.get("/children/stats")
async def get_children_stats(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed stats for all children in family"""
    from app.models.daily_progress import DailyProgress
    from app.models.task_assignment import TaskAssignment
    from app.models.task_approval import TaskApproval, ApprovalStatus
    from datetime import date
    from sqlalchemy import func

    if not current_user or not current_user.family_id:
        return {"children_stats": []}

    children = db.query(Profile).filter(
        Profile.family_id == current_user.family_id,
        Profile.role == "child"
    ).all()

    today = date.today()
    children_stats = []

    for child in children:
        # Get today's progress
        today_progress = db.query(DailyProgress).filter(
            DailyProgress.child_id == child.id,
            DailyProgress.date == today
        ).first()

        # Calculate stats
        tasks_completed_today = len(today_progress.completed_task_ids) if today_progress and today_progress.completed_task_ids else 0
        points_earned_today = today_progress.total_points if today_progress else 0
        pending_approvals_count = len(today_progress.pending_approval_ids) if today_progress and today_progress.pending_approval_ids else 0

        # Get total rewards claimed (count all redeemed rewards across all days)
        # Fetch all daily progress records with redeemed rewards
        all_progress = db.query(DailyProgress).filter(
            DailyProgress.child_id == child.id,
            DailyProgress.redeemed_reward_ids.isnot(None)
        ).all()

        # Count unique rewards across all days
        all_rewards = set()
        for progress in all_progress:
            if progress.redeemed_reward_ids:
                all_rewards.update(progress.redeemed_reward_ids)
        total_rewards_claimed = len(all_rewards)

        # Get tasks assigned to this child
        assigned_tasks_count = db.query(TaskAssignment).filter(
            TaskAssignment.child_id == child.id
        ).count()

        # Get last activity date (most recent daily progress entry)
        last_activity = db.query(DailyProgress).filter(
            DailyProgress.child_id == child.id
        ).order_by(DailyProgress.date.desc()).first()

        last_activity_date = last_activity.date.isoformat() if last_activity else None

        # Calculate completion rate (tasks completed today vs assigned)
        completion_rate = 0
        if assigned_tasks_count > 0 and tasks_completed_today > 0:
            completion_rate = min(100, round((tasks_completed_today / assigned_tasks_count) * 100))

        children_stats.append({
            "id": child.id,
            "first_name": child.first_name,
            "last_name": child.last_name,
            "theme": child.theme,
            "total_lifetime_points": child.total_lifetime_points,
            "tasks_completed_today": tasks_completed_today,
            "points_earned_today": points_earned_today,
            "pending_approvals": pending_approvals_count,
            "total_rewards_claimed": total_rewards_claimed,
            "assigned_tasks_count": assigned_tasks_count,
            "completion_rate": completion_rate,
            "last_activity_date": last_activity_date
        })

    return {"children_stats": children_stats}