# ==============================================================================
# FILE: app/api/__init__.py
# ==============================================================================

# Empty file to make this a package


# ==============================================================================
# FILE: app/api/auth.py
# Authentication endpoints - Login, Register, Logout
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.auth import UserLogin, UserRegister, Token, FamilyCreate
from app.models.profile import Profile, UserRole
from app.models.family import Family
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user
from app.utils.helpers import generate_join_code
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Register new user and optionally create or join family
    
    If join_code provided: Join existing family as child
    If no join_code: Create new family as admin
    """
    
    # Check if email already exists
    existing_user = db.query(Profile).filter(Profile.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Handle family join or creation
    if user_data.join_code:
        # Join existing family
        family = db.query(Family).filter(Family.join_code == user_data.join_code).first()
        if not family:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid join code"
            )
        
        # Create child profile
        new_user = Profile(
            family_id=family.id,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=UserRole.CHILD
        )
        
    else:
        # Create new family first
        new_family = Family(
            name=f"{user_data.first_name}'s Family",
            join_code=generate_join_code()
        )
        db.add(new_family)
        db.flush()
        
        # Create admin profile
        new_user = Profile(
            family_id=new_family.id,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=UserRole.ADMIN
        )
        db.add(new_user)
        db.flush()
        
        # Set admin_id on family
        new_family.admin_id = new_user.id
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    Returns JWT token and sets httpOnly cookie
    """
    
    # Find user
    user = db.query(Profile).filter(Profile.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    """
    Logout by clearing the cookie
    """
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    """
    # Get family info
    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role.value,
        "theme": current_user.theme,
        "total_lifetime_points": current_user.total_lifetime_points,
        "family": {
            "id": family.id,
            "name": family.name,
            "join_code": family.join_code if current_user.role in [UserRole.ADMIN, UserRole.PARENT] else None
        }
    }


@router.post("/family/create")
async def create_family(
    family_data: FamilyCreate,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new family (admin only)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create families"
        )
    
    new_family = Family(
        name=family_data.family_name,
        join_code=generate_join_code(),
        admin_id=current_user.id
    )
    
    db.add(new_family)
    db.commit()
    db.refresh(new_family)
    
    return {
        "id": new_family.id,
        "name": new_family.name,
        "join_code": new_family.join_code
    }