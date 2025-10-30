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
