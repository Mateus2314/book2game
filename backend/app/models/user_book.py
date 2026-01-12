from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserBook(Base):
    """
    User's personal book library.
    Many-to-many relationship between users and books with additional metadata.
    """
    
    __tablename__ = "user_books"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    
    # Personal metadata
    is_favorite = Column(Boolean, default=False, nullable=False)
    reading_status = Column(String(20), default="to_read", nullable=False)  # to_read, reading, finished
    personal_rating = Column(Integer, nullable=True)  # 1-5 stars
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="library")
    book = relationship("Book", backref="user_libraries")
    
    # Unique constraint: user can't have same book twice
    __table_args__ = (
        {"schema": None},
    )
    
    def __repr__(self):
        return f"<UserBook(user_id={self.user_id}, book_id={self.book_id})>"
