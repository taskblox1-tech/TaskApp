from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class TaskPeriod(str, enum.Enum):
    """When task should be completed"""
    MORNING = "morning"
    EVENING = "evening"
    ANYTIME = "anytime"


class TaskCategory(str, enum.Enum):
    """Task categorization"""
    DAILY = "DAILY"
    BONUS = "BONUS"
    GENERAL = "GENERAL"
    MORNING_ROUTINE = "Morning Routine"
    BEDROOM_CARE = "Bedroom Care"
    BATHROOM_DUTIES = "Bathroom Duties"
    HYGIENE = "Hygiene"
    HOMEWORK_LEARNING = "Homework & Learning"
    CHORES = "Chores"
    PET_CARE = "Pet Care"
    SPECIAL_TASKS = "Special Tasks"


class TaskDayType(str, enum.Enum):
    """Which days task applies to"""
    ANYDAY = "anyday"
    WEEKDAY = "weekday"
    WEEKEND = "weekend"


class Task(Base):
    """Task that can be assigned to children"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    points = Column(Integer, default=10, nullable=False)
    icon = Column(String(10), default="✅")
    period = Column(SQLEnum(TaskPeriod), default=TaskPeriod.ANYTIME, nullable=False)
    category = Column(SQLEnum(TaskCategory), default=TaskCategory.CHORES, nullable=False, index=True)
    day_type = Column(SQLEnum(TaskDayType), default=TaskDayType.WEEKDAY, nullable=False)
    requires_approval = Column(Integer, default=0, nullable=False)
    library_category = Column(String(50))
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    family = relationship("Family", back_populates="tasks")
    assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")
    approvals = relationship("TaskApproval", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task {self.title} ({self.points}pts)>"
    