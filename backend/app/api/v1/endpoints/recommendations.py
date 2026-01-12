import json
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import recommendation as crud_recommendation
from app.models.user import User
from app.schemas.recommendation import Recommendation, RecommendationCreate
from app.services.recommendation_service import recommendation_service

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per user
async def generate_recommendation(
    request: Request,
    recommendation_in: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    **MAIN ENDPOINT**: Generate game recommendations based on a book using AI.
    
    Pipeline:
    1. Fetch book from Google Books
    2. Extract features (genre, themes, author)
    3. Classify with Hugging Face AI (30s timeout, 3 retries)
    4. Map literary genres → game tags
    5. Generate real games using Llama 3.1 8B Instruct
    6. Calculate similarity scores
    7. Save to database with cache
    
    **Rate limit**: 5 requests/minute per user (AI operations are expensive).
    """
    try:
        start_time = time.time()
        
        result = await recommendation_service.generate_recommendation(
            db=db,
            user_id=current_user.id,
            book_id=recommendation_in.book_id,
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "recommendation_id": result["recommendation"].id,
            "book": result["book_data"],
            "recommended_games": result["games"],
            "ai_generated": result["recommendation"].ai_generated,
            "similarity_score": result["recommendation"].similarity_score,
            "processing_time_ms": processing_time,
            "message": "Recommendation generated successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendation: {str(e)}",
        )


@router.get("/", response_model=List[Recommendation])
async def list_recommendations(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Recommendation]:
    """
    List all recommendations for the current user.
    
    Ordered by creation date (newest first).
    """
    recommendations = crud_recommendation.get_user_recommendations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    
    return recommendations


@router.get("/{recommendation_id}", response_model=Dict[str, Any])
async def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get detailed information about a specific recommendation.
    
    Includes book data and full game details.
    """
    recommendation = crud_recommendation.get_recommendation(db, recommendation_id)
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )
    
    # Verify ownership
    if recommendation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this recommendation",
        )
    
    # Parse games JSON
    games_data = json.loads(recommendation.games)
    
    return {
        "id": recommendation.id,
        "book_id": recommendation.book_id,
        "games": games_data,
        "ai_generated": recommendation.ai_generated,
        "similarity_score": recommendation.similarity_score,
        "processing_time_ms": recommendation.processing_time_ms,
        "created_at": recommendation.created_at,
    }
