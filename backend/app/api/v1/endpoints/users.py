from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import recommendation as crud_recommendation
from app.crud import user as crud_user
from app.crud import user_book as crud_user_book
from app.crud import user_game as crud_user_game
from app.crud import book as crud_book
from app.crud import game as crud_game
from app.models.user import User
from app.schemas.recommendation import Recommendation
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate
from app.schemas.user_book import UserBook, UserBookUpdate, UserBookWithBook
from app.schemas.user_game import UserGame, UserGameUpdate, UserGameWithGame
from app.services.external import google_books_service


router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Update current user profile (email, full_name, password)."""
    from sqlalchemy.exc import IntegrityError
    
    # Check if email is being updated and already exists
    if user_update.email:
        existing_user = crud_user.get_user_by_email(db, email=user_update.email.lower())
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    try:
        updated_user = crud_user.update_user(db, current_user, user_update)
        return updated_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )


@router.get("/me/recommendations", response_model=List[Recommendation])
async def get_user_recommendations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Recommendation]:
    """Get all recommendations for current user."""
    recommendations = crud_recommendation.get_user_recommendations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return recommendations


# ============================================
# USER LIBRARY ENDPOINTS
# ============================================


@router.get("/me/books", response_model=List[UserBookWithBook])
async def get_my_library(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    favorite_only: bool = Query(False, description="Show only favorites"),
    reading_status: Optional[str] = Query(None, pattern="^(to_read|reading|finished)$", description="Filter by reading status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserBookWithBook]:
    """
    Get my personal book library.
    
    - **skip**: Pagination offset
    - **limit**: Maximum results (1-100)
    - **favorite_only**: Filter only favorites
    - **reading_status**: Filter by status (to_read, reading, finished)
    """
    user_books = crud_user_book.get_user_books(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        favorite_only=favorite_only,
        reading_status=reading_status,
    )
    return [UserBookWithBook.model_validate(ub) for ub in user_books]

@router.post("/me/books/from-google/{google_books_id}", response_model=UserBookWithBook, status_code=status.HTTP_201_CREATED)
async def add_book_to_library_from_google(
    google_books_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserBookWithBook:
    """
    Add book to my library from Google Books API.
    
    Automatically:
    1. Fetches book data from Google Books API
    2. Creates book in database (if doesn't exist)
    3. Adds to your personal library
    
    - **google_books_id**: Google Books ID (e.g., "wrOQLV6xB-wC")
    
    **Usage:** After searching books with `/books/search`, use this endpoint
    to add a book to your personal collection.
    """
    # 1. Check if book exists in global books table
    book = crud_book.get_book_by_google_id(db, google_books_id)
    
    # 2. If doesn't exist, fetch from Google Books and create
    if not book:
        google_data = await google_books_service.get_details(google_books_id)
        
        if not google_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with Google Books ID '{google_books_id}' not found in Google Books API",
            )
        
        # Parse and create book
        from app.schemas.book import BookCreate
        parsed_data = google_books_service.parse_book_data(google_data)
        
        if not parsed_data.get("title"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Book data from Google Books API is missing required field: title",
            )
        
        book_in = BookCreate(**parsed_data)
        book = crud_book.create_book(db, book_in)
    
    # 3. Add to user's library (or return existing)
    user_book = crud_user_book.add_to_library(db, user_id=current_user.id, book_id=book.id)
    
    return user_book


@router.post("/me/books/{book_id}", response_model=UserBookWithBook, status_code=status.HTTP_201_CREATED)
async def add_book_to_library(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserBookWithBook:
    """
    Add existing book to my library by book_id.
    
    Book must already exist in the global books table.
    Use `/me/books/from-google/{google_books_id}` for automatic creation.
    
    - **book_id**: Internal book ID from database
    """
    # Verify book exists
    book = crud_book.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    
    # Add to library
    user_book = crud_user_book.add_to_library(db, user_id=current_user.id, book_id=book_id)
    
    return user_book


@router.put("/me/books/{book_id}", response_model=UserBookWithBook)
async def update_library_book(
    book_id: int,
    user_book_update: UserBookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserBookWithBook:
    """
    Update book metadata in my library.
    
    - **book_id**: Internal book ID
    - **is_favorite**: Mark as favorite
    - **reading_status**: to_read, reading, or finished
    - **personal_rating**: 1-5 stars
    - **notes**: Personal notes about the book
    """
    user_book = crud_user_book.update_user_book(
        db=db,
        user_id=current_user.id,
        book_id=book_id,
        update_data=user_book_update,
    )
    
    if not user_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found in your library",
        )
    
    return user_book


@router.delete("/me/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book_from_library(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove book from my library.
    
    Note: This only removes from YOUR library, not from the global books table.
    
    - **book_id**: Internal book ID
    """
    deleted = crud_user_book.remove_from_library(db, user_id=current_user.id, book_id=book_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found in your library",
        )
    
    return None


# ============================================
# USER GAME LIBRARY ENDPOINTS
# ============================================


@router.get("/me/games", response_model=List[UserGameWithGame])
async def get_my_game_library(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records"),
    favorite_only: bool = Query(False, description="Show only favorites"),
    play_status: Optional[str] = Query(None, pattern="^(to_play|playing|completed)$", description="Filter by play status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserGameWithGame]:
    """
    Get my personal game library.
    
    - **skip**: Pagination offset
    - **limit**: Maximum results (1-100)
    - **favorite_only**: Filter only favorites
    - **play_status**: Filter by status (to_play, playing, completed)
    """
    user_games = crud_user_game.get_user_games(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        favorite_only=favorite_only,
        play_status=play_status,
    )
    return user_games


@router.post("/me/games/{game_id}", response_model=UserGameWithGame, status_code=status.HTTP_201_CREATED)
async def add_game_to_library(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserGameWithGame:
    """
    Add existing game to my library by game_id.
    
    Game must already exist in the global games table (created via recommendations).
    
    - **game_id**: Internal game ID from database
    """
    # Verify game exists
    game = crud_game.get_game(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with ID {game_id} not found",
        )
    
    # Add to library
    user_game = crud_user_game.add_to_library(db, user_id=current_user.id, game_id=game_id)
    
    return user_game


@router.put("/me/games/{game_id}", response_model=UserGameWithGame)
async def update_library_game(
    game_id: int,
    user_game_update: UserGameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserGameWithGame:
    """
    Update game metadata in my library.
    
    - **game_id**: Internal game ID
    - **is_favorite**: Mark as favorite
    - **play_status**: to_play, playing, or completed
    - **personal_rating**: 1-5 stars
    - **notes**: Personal notes about the game
    - **hours_played**: Hours played
    """
    user_game = crud_user_game.update_user_game(
        db=db,
        user_id=current_user.id,
        game_id=game_id,
        update_data=user_game_update,
    )
    
    if not user_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with ID {game_id} not found in your library",
        )
    
    return user_game


@router.delete("/me/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_game_from_library(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove game from my library.
    
    Note: This only removes from YOUR library, not from the global games table.
    
    - **game_id**: Internal game ID
    """
    deleted = crud_user_game.remove_from_library(db, user_id=current_user.id, game_id=game_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with ID {game_id} not found in your library",
        )
    
    return None
