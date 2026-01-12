from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate


def get_game(db: Session, game_id: int) -> Optional[Game]:
    """Get game by ID."""
    return db.query(Game).filter(Game.id == game_id).first()


def get_game_by_rawg_id(db: Session, rawg_id: int) -> Optional[Game]:
    """Get game by unique game ID (AI-generated)."""
    return db.query(Game).filter(Game.rawg_id == rawg_id).first()


def create_game(db: Session, game_in: GameCreate) -> Game:
    """Create new game."""
    db_game = Game(**game_in.model_dump())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


def update_game(db: Session, game: Game, game_in: GameUpdate) -> Game:
    """Update game."""
    update_data = game_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(game, field, value)
    
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def get_or_create_game(db: Session, game_in: GameCreate) -> Game:
    """Get existing game or create new one."""
    existing_game = get_game_by_rawg_id(db, game_in.rawg_id)
    if existing_game:
        return existing_game
    return create_game(db, game_in)


def search_games(db: Session, query: str, skip: int = 0, limit: int = 10) -> List[Game]:
    """Search games by name (case-insensitive)."""
    return (
        db.query(Game)
        .filter(Game.name.ilike(f"%{query}%"))
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_games(db: Session, query: str) -> int:
    """Count games matching search query."""
    return db.query(func.count(Game.id)).filter(Game.name.ilike(f"%{query}%")).scalar()


def search_by_tags(db: Session, tags: List[str], skip: int = 0, limit: int = 10) -> List[Game]:
    """Search games by tags (OR logic - matches any tag)."""
    filters = [Game.tags.ilike(f"%{tag}%") for tag in tags]
    return (
        db.query(Game)
        .filter(or_(*filters))
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_by_tags(db: Session, tags: List[str]) -> int:
    """Count games matching any of the tags."""
    filters = [Game.tags.ilike(f"%{tag}%") for tag in tags]
    return db.query(func.count(Game.id)).filter(or_(*filters)).scalar()
