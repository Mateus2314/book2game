from fastapi import APIRouter

from app.api.v1.endpoints import auth, books, games, recommendations, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(books.router, prefix="/books", tags=["Books"])
api_router.include_router(games.router, prefix="/games", tags=["Games"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
