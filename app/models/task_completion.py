"""
Task Completion Model - Detailed tracking for analytics
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class TaskCompletion(Base):
    """
    Detailed record of each task completion for analytics
    Stores snapshot of task metadata at completion time
    """
    __tablename__ = "task_completions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("profiles.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)

    # Task metadata (snapshot at completion time)
    task_title = Column(String(200), nullable=False)
    task_category = Column(String(50), nullable=False)  # chores, academic, health, etc.
    task_period = Column(String(20), nullable=False)  # morning, evening, anytime
    points_earned = Column(Integer, nullable=False)

    # Completion details
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completion_date = Column(Date, nullable=False, index=True)  # For quick date queries

    # Was it approved or instant?
    required_approval = Column(Integer, default=0)  # 1 if required approval

    # Relationships
    child = relationship("Profile", foreign_keys=[child_id])
    task = relationship("Task", foreign_keys=[task_id])
    family = relationship("Family", foreign_keys=[family_id])

    def __repr__(self):
        return f"<TaskCompletion {self.task_title} by child_id={self.child_id} on {self.completion_date}>"
