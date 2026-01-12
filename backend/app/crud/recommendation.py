from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationCreate


def get_recommendation(db: Session, recommendation_id: int) -> Optional[Recommendation]:
    """Get recommendation by ID."""
    return db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()


def get_user_recommendations(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Recommendation]:
    """Get all recommendations for a user."""
    return (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_recommendation(
    db: Session,
    user_id: int,
    book_id: int,
    games: str,
    ai_generated: bool = True,
    similarity_score: Optional[float] = None,
    processing_time_ms: Optional[int] = None,
) -> Recommendation:
    """Create new recommendation."""
    db_recommendation = Recommendation(
        user_id=user_id,
        book_id=book_id,
        games=games,
        ai_generated=ai_generated,
        similarity_score=similarity_score,
        processing_time_ms=processing_time_ms,
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation
