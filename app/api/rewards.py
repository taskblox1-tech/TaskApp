"""
Rewards API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile
from app.models.reward import Reward

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