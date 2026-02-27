from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import book as crud_book
from app.models.user import User
from app.schemas.book import Book, BookCreate
from app.services.external import google_books_service
from app.services.external.google_books_mapper import google_json_to_book

router = APIRouter()


@router.get("/search", response_model=Dict[str, Any])
async def search_books(
    query: str = Query(..., min_length=1, max_length=200, description="Search query"),
    max_results: int = Query(10, ge=1, le=40, description="Maximum results"),
    start_index: int = Query(0, ge=0, description="Start index for pagination"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Search books using Google Books API with caching (TTL 24h).
    
    - **query**: Search term (title, author, ISBN, etc.)
    - **max_results**: Number of results (1-40)
    - **start_index**: Pagination offset
    """
    try:
        results = await google_books_service.search(
            query=query,
            max_results=max_results,
            start_index=start_index,
        )

        items = results.get("items", [])
        mapped_items = [google_json_to_book(item) for item in items]

        return {
            "total_items": results.get("totalItems", 0),
            "items": mapped_items,
            "query": query,
            "max_results": max_results,
            "start_index": start_index,
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Books API error: {str(e)}",
        )


@router.get("/{book_id}", response_model=Dict[str, Any])
async def get_book_details(
    book_id: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get detailed information about a specific book by Google Books ID.
    
    - **book_id**: Google Books ID (e.g., "zyTCAlFPjgYC")
    """
    try:
        book_data = await google_books_service.get_details(book_id)
        
        if not book_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID '{book_id}' not found",
            )
        
        return book_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Books API error: {str(e)}",
        )


@router.post("/from-google/{google_books_id}", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book_from_google(
    google_books_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Book:
    """
    Create a book in the local database from Google Books API.
    
    Automatically fetches book data from Google Books API and saves to database.
    If book already exists (by google_books_id), returns existing record.
    
    - **google_books_id**: Google Books ID (e.g., "wrOQLV6xB-wC")
    
    **Usage:** After searching books with `/books/search`, use this endpoint 
    to save a book to your collection by providing its google_books_id.
    """
    # Check if book already exists
    existing_book = crud_book.get_book_by_google_id(db, google_books_id)
    if existing_book:
        return existing_book
    
    # Fetch book data from Google Books API
    try:
        google_data = await google_books_service.get_details(google_books_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google Books API error: {str(e)}",
        )
    
    if not google_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with Google Books ID '{google_books_id}' not found in Google Books API",
        )
    
    # Parse and transform data to BookCreate schema
    parsed_data = google_books_service.parse_book_data(google_data)
    
    # Validate required fields
    if not parsed_data.get("title"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Book data from Google Books API is missing required field: title",
        )
    
    # Create BookCreate instance
    book_in = BookCreate(**parsed_data)
    
    # Save to database
    book = crud_book.create_book(db, book_in)
    
    return book


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Book:
    """
    Create a book in the local database (manual data entry).
    
    Used internally when generating recommendations.
    Creates or retrieves existing book by google_books_id.
    """
    existing_book = crud_book.get_book_by_google_id(db, book_in.google_books_id)
    
    if existing_book:
        return existing_book
    
    book = crud_book.create_book(db, book_in)
    return book
