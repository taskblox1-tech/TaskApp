from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class RewardType(str, enum.Enum):
    """Type of reward"""
    SCREEN_TIME = "screen_time"
    TREAT = "treat"
    ACTIVITY = "activity"
    ALLOWANCE = "allowance"
    SPECIAL = "special"
    PRIVILEGE = "privilege"


class Reward(Base):
    """Reward that can be redeemed with points"""
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    cost = Column(Integer, nullable=False)
    icon = Column(String(10), default="🎁")
    type = Column(SQLEnum(RewardType), default=RewardType.SPECIAL, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    family = relationship("Family", back_populates="rewards")
    
    def __repr__(self):
        return f"<Reward {self.name} ({self.cost}pts)>"