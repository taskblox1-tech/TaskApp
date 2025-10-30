from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

from app.database import Base


class ApprovalStatus(str, enum.Enum):
    """Status of approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class TaskApproval(Base):
    """Approval request for tasks that require parent/teacher/coach verification"""
    __tablename__ = "task_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("profiles.id"), nullable=False, index=True)
    date_for = Column(Date, default=date.today, nullable=False, index=True)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)
    proof_text = Column(Text)
    notes = Column(Text)
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("profiles.id"))
    
    # Relationships
    task = relationship("Task", back_populates="approvals")
    child = relationship("Profile", foreign_keys=[child_id], back_populates="approval_requests")
    approver = relationship("Profile", foreign_keys=[approved_by], back_populates="approvals_given")
    
    def __repr__(self):
        return f"<TaskApproval task={self.task_id} status={self.status.value}>"