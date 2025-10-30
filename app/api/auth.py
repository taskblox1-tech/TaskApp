"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
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