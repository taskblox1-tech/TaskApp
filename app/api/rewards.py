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