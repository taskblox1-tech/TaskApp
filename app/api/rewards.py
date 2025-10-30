"""
Rewards API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile
from app.models.reward import Reward, RewardType

router = APIRouter()

@router.get("/")
async def get_rewards(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available rewards"""
    if not current_user or not current_user.family_id:
        return {"rewards": []}

    rewards = db.query(Reward).filter(
        Reward.family_id == current_user.family_id
    ).all()

    return {
        "rewards": [
            {
                "id": r.id,
                "name": r.name,
                "cost": r.cost,
                "icon": r.icon,
                "type": r.type.value,
                "is_active": bool(r.is_active)
            }
            for r in rewards
        ]
    }


@router.post("/")
async def create_reward(
    reward_data: dict,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reward (parent only)"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can create rewards")

    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="No family found")

    # Create the reward
    new_reward = Reward(
        family_id=current_user.family_id,
        name=reward_data.get("name"),
        cost=reward_data.get("cost", 100),
        icon=reward_data.get("icon", "🎁"),
        type=RewardType(reward_data.get("type", "prize")),
        is_active=1
    )

    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)

    return {
        "id": new_reward.id,
        "name": new_reward.name,
        "message": "Reward created successfully!"
    }


@router.put("/{reward_id}")
async def update_reward(
    reward_id: int,
    reward_data: dict,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a reward (parent only)"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can update rewards")

    # Verify reward exists and belongs to family
    reward = db.query(Reward).filter(
        Reward.id == reward_id,
        Reward.family_id == current_user.family_id
    ).first()

    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    # Update reward fields
    if "name" in reward_data:
        reward.name = reward_data["name"]
    if "cost" in reward_data:
        reward.cost = reward_data["cost"]
    if "icon" in reward_data:
        reward.icon = reward_data["icon"]
    if "type" in reward_data:
        reward.type = RewardType(reward_data["type"])

    db.commit()
    return {"message": "Reward updated successfully!"}


@router.delete("/{reward_id}")
async def delete_reward(
    reward_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a reward (parent only)"""
    if current_user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can delete rewards")

    # Verify reward exists and belongs to family
    reward = db.query(Reward).filter(
        Reward.id == reward_id,
        Reward.family_id == current_user.family_id
    ).first()

    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    # Delete the reward
    db.delete(reward)
    db.commit()

    return {"message": "Reward deleted successfully!"}


@router.post("/{reward_id}/redeem")
async def redeem_reward(
    reward_id: int,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redeem a reward with points"""
    from app.models.daily_progress import DailyProgress
    from datetime import date
    from sqlalchemy.orm.attributes import flag_modified

    # Verify reward exists and belongs to family
    reward = db.query(Reward).filter(
        Reward.id == reward_id,
        Reward.family_id == current_user.family_id,
        Reward.is_active == 1
    ).first()

    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")

    # Check if user has enough points
    if current_user.total_lifetime_points < reward.cost:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough points! You need {reward.cost} points but only have {current_user.total_lifetime_points}."
        )

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

    # Add reward to redeemed list
    if progress.redeemed_reward_ids is None:
        progress.redeemed_reward_ids = []

    progress.redeemed_reward_ids.append(reward_id)
    flag_modified(progress, 'redeemed_reward_ids')

    # Deduct points from user's total
    current_user.total_lifetime_points -= reward.cost

    db.commit()

    return {
        "message": f"Congratulations! You redeemed {reward.name}!",
        "reward_name": reward.name,
        "points_spent": reward.cost,
        "remaining_points": current_user.total_lifetime_points
    }


@router.get("/redeemed")
async def get_redeemed_rewards(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of redeemed rewards for current user"""
    from app.models.daily_progress import DailyProgress

    # Get all progress records with redeemed rewards
    progress_records = db.query(DailyProgress).filter(
        DailyProgress.child_id == current_user.id,
        DailyProgress.redeemed_reward_ids.isnot(None)
    ).order_by(DailyProgress.date.desc()).all()

    # Build list of redeemed rewards with dates
    redeemed_list = []
    for progress in progress_records:
        if progress.redeemed_reward_ids:
            for reward_id in progress.redeemed_reward_ids:
                reward = db.query(Reward).filter(Reward.id == reward_id).first()
                if reward:
                    redeemed_list.append({
                        "id": reward.id,
                        "name": reward.name,
                        "cost": reward.cost,
                        "icon": reward.icon,
                        "redeemed_date": progress.date.isoformat()
                    })

    return {"redeemed_rewards": redeemed_list}