"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str
    name: str
    role: str  # "parent", "child", "teacher", "coach"
    family_id: Optional[int] = None
    join_code: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User data response"""
    id: int
    email: str
    name: str
    role: str
    family_id: Optional[int]
    theme: Optional[str]
    total_points: int
    
    class Config:
        from_attributes = True