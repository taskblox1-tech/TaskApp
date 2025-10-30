from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date

from app.database import Base


class DailyProgress(Base):
    """Daily progress tracking for each child"""
    __tablename__ = "daily_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("profiles.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False, index=True)
    total_points = Column(Integer, default=0, nullable=False)
    completed_task_ids = Column(JSON, default=list)
    pending_approval_ids = Column(JSON, default=list)
    redeemed_reward_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # One progress record per child per day
    __table_args__ = (
        UniqueConstraint('child_id', 'date', name='uq_child_date'),
    )
    
    # Relationships
    child = relationship("Profile", back_populates="daily_progress")
    
    def __repr__(self):
        return f"<DailyProgress child={self.child_id} date={self.date} points={self.total_points}>"