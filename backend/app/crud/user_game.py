from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.user_game import UserGame
from app.schemas.user_game import UserGameCreate, UserGameUpdate


def get_user_games(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    favorite_only: bool = False,
    play_status: Optional[str] = None,
) -> List[UserGame]:
    """
    Get user's game library with optional filters.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        favorite_only: Filter only favorites
        play_status: Filter by play status (to_play, playing, completed)
    
    Returns:
        List of UserGame instances
    """
    query = db.query(UserGame).filter(UserGame.user_id == user_id)
    
    if favorite_only:
        query = query.filter(UserGame.is_favorite == True)
    
    if play_status:
        query = query.filter(UserGame.play_status == play_status)
    
    return query.order_by(UserGame.created_at.desc()).offset(skip).limit(limit).all()


def get_user_game(db: Session, user_id: int, game_id: int) -> Optional[UserGame]:
    """
    Get specific game from user's library.
    
    Args:
        db: Database session
        user_id: User ID
        game_id: Game ID
    
    Returns:
        UserGame instance or None
    """
    return (
        db.query(UserGame)
        .filter(UserGame.user_id == user_id, UserGame.game_id == game_id)
        .first()
    )


def get_user_game_by_id(db: Session, user_game_id: int, user_id: int) -> Optional[UserGame]:
    """
    Get user game by ID with ownership verification.
    
    Args:
        db: Database session
        user_game_id: UserGame ID
        user_id: User ID (for ownership verification)
    
    Returns:
        UserGame instance or None
    """
    return (
        db.query(UserGame)
        .filter(UserGame.id == user_game_id, UserGame.user_id == user_id)
        .first()
    )


def add_to_library(db: Session, user_id: int, game_id: int) -> UserGame:
    """
    Add game to user's library.
    
    If game already exists in library, returns existing record.
    
    Args:
        db: Database session
        user_id: User ID
        game_id: Game ID
    
    Returns:
        UserGame instance
    """
    # Check if already exists
    existing = get_user_game(db, user_id, game_id)
    if existing:
        return existing
    
    # Create new entry
    user_game = UserGame(user_id=user_id, game_id=game_id)
    db.add(user_game)
    db.commit()
    db.refresh(user_game)
    return user_game


def update_user_game(
    db: Session,
    user_id: int,
    game_id: int,
    update_data: UserGameUpdate,
) -> Optional[UserGame]:
    """
    Update user game metadata.
    
    Args:
        db: Database session
        user_id: User ID
        game_id: Game ID
        update_data: Update data
    
    Returns:
        Updated UserGame or None if not found
    """
    user_game = get_user_game(db, user_id, game_id)
    if not user_game:
        return None
    
    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user_game, field, value)
    
    db.commit()
    db.refresh(user_game)
    return user_game


def remove_from_library(db: Session, user_id: int, game_id: int) -> bool:
    """
    Remove game from user's library.
    
    Args:
        db: Database session
        user_id: User ID
        game_id: Game ID
    
    Returns:
        True if deleted, False if not found
    """
    result = (
        db.query(UserGame)
        .filter(UserGame.user_id == user_id, UserGame.game_id == game_id)
        .delete()
    )
    db.commit()
    return result > 0


def count_user_games(db: Session, user_id: int) -> int:
    """
    Count total games in user's library.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Number of games
    """
    return db.query(UserGame).filter(UserGame.user_id == user_id).count()
