from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class TaskAssignment(Base):
    """Assignment of a task to a specific child"""
    __tablename__ = "task_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("profiles.id"), nullable=False, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Prevent duplicate assignments
    __table_args__ = (
        UniqueConstraint('task_id', 'child_id', name='uq_task_child'),
    )
    
    # Relationships
    task = relationship("Task", back_populates="assignments")
    child = relationship("Profile", back_populates="task_assignments")
    
    def __repr__(self):
        return f"<TaskAssignment task={self.task_id} child={self.child_id}>"