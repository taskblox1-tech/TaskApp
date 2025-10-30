from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User roles within a family"""
    ADMIN = "admin"
    PARENT = "parent"
    CHILD = "child"
    TEACHER = "teacher"
    COACH = "coach"


class Profile(Base):
    """User profile (parent, child, teacher, coach)"""
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.CHILD, nullable=False)
    theme = Column(String(50), default="minecraft")
    avatar = Column(String(100), nullable=True)  # Avatar choice within theme
    avatar_url = Column(String(500))
    theme_enabled = Column(Boolean, default=False, nullable=False)  # Whether custom theme is enabled
    custom_colors = Column(JSON, nullable=True)  # Custom color scheme for parents
    current_streak = Column(Integer, default=0, nullable=False)  # Consecutive days completing tasks
    longest_streak = Column(Integer, default=0, nullable=False)  # Best streak ever
    total_lifetime_points = Column(Integer, default=0, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    family = relationship("Family", back_populates="members", foreign_keys=[family_id])
    daily_progress = relationship("DailyProgress", back_populates="child", cascade="all, delete-orphan")
    task_assignments = relationship("TaskAssignment", back_populates="child", cascade="all, delete-orphan")
    approval_requests = relationship(
        "TaskApproval",
        foreign_keys="TaskApproval.child_id",
        back_populates="child",
        cascade="all, delete-orphan"
    )
    approvals_given = relationship(
        "TaskApproval",
        foreign_keys="TaskApproval.approved_by",
        back_populates="approver"
    )
    character_unlocks = relationship("CharacterUnlock", back_populates="child", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Profile {self.first_name} ({self.role.value})>"