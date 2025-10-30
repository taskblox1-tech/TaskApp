"""
Character unlock tracking model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class CharacterUnlock(Base):
    """Tracks which characters each child has unlocked"""
    __tablename__ = "character_unlocks"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    character_key = Column(String(100), nullable=False)  # e.g., "minecraft_steve", "mario_luigi"
    theme_key = Column(String(50), nullable=False)  # e.g., "minecraft", "mario"
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    unlock_method = Column(String(100))  # e.g., "default", "streak_7", "points_500", "academic_achievement"

    # Relationships
    child = relationship("Profile", back_populates="character_unlocks")

    def __repr__(self):
        return f"<CharacterUnlock(child_id={self.child_id}, character={self.character_key})>"
