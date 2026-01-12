from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserGame(Base):
    """
    User's personal game library.
    Many-to-many relationship between users and games with additional metadata.
    """
    
    __tablename__ = "user_games"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    
    # Personal metadata
    is_favorite = Column(Boolean, default=False, nullable=False)
    play_status = Column(String(20), default="to_play", nullable=False)  # to_play, playing, completed
    personal_rating = Column(Integer, nullable=True)  # 1-5 stars
    notes = Column(Text, nullable=True)
    hours_played = Column(Integer, nullable=True)  # Tempo jogado em horas
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="game_library")
    game = relationship("Game", backref="user_libraries")
    
    def __repr__(self):
        return f"<UserGame(user_id={self.user_id}, game_id={self.game_id})>"
