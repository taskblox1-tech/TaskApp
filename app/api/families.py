# ============= app/api/families.py =============
"""
Families API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.profile import Profile

router = APIRouter()

@router.get("/mine")
async def get_my_family(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's family"""
    if not current_user.family:
        return {"family": None}
    
    family = current_user.family
    members = db.query(Profile).filter(Profile.family_id == family.id).all()
    
    return {
        "family": {
            "id": family.id,
            "name": family.name,
            "join_code": family.join_code,
            "members": [
                {
                    "id": m.id,
                    "first_name": m.first_name,
                    "last_name": m.last_name,
                    "role": m.role.value,
                    "theme": m.theme,
                    "total_points": m.total_lifetime_points
                }
                for m in members
            ]
        }
    }
