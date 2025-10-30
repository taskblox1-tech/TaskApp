from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Family(Base):
    """Family/household group"""
    __tablename__ = "families"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    join_code = Column(String(20), unique=True, nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("Profile", back_populates="family", foreign_keys="Profile.family_id")
    admin = relationship("Profile", foreign_keys=[admin_id], post_update=True)
    tasks = relationship("Task", back_populates="family", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="family", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Family {self.name} ({self.join_code})>"