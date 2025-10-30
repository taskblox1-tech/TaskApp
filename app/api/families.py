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

@router.get("/my-family")
@router.get("/mine")
async def get_my_family(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's family"""
    if not current_user or not current_user.family:
        return {"family": None, "join_code": None}

    family = current_user.family

    return {
        "id": family.id,
        "name": family.name,
        "join_code": family.join_code
    }


@router.get("/members")
async def get_family_members(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of the current user's family with their last login"""
    if not current_user or not current_user.family_id:
        return {"members": []}

    # Get all family members
    members = db.query(Profile).filter(
        Profile.family_id == current_user.family_id
    ).order_by(Profile.role.desc(), Profile.first_name).all()

    return {
        "members": [
            {
                "id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "email": member.email,
                "role": member.role,
                "theme": member.theme if member.theme else "default",
                "total_lifetime_points": member.total_lifetime_points,
                "last_login": member.last_login.isoformat() if member.last_login else None,
                "is_current_user": member.id == current_user.id
            }
            for member in members
        ]
    }
