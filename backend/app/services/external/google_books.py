from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.services.cache_service import cache_service

logger = get_logger()


class GoogleBooksService:
    """
    Google Books API service with caching.
    
    Endpoints:
    - search: Search books by query
    - get_details: Get book details by ID
    
    Cache: TTL 24h (livros raramente mudam)
    """

    def __init__(self):
        self.base_url = settings.GOOGLE_BOOKS_BASE_URL
        self.api_key = settings.GOOGLE_BOOKS_API_KEY
        self.timeout = 10.0

    async def search(
        self,
        query: str,
        max_results: int = 10,
        start_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Search books by query.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            start_index: Starting index for pagination
            
        Returns:
            Dictionary with search results
        """
        # Check cache
        cache_key = f"google_books:search:{query}:{max_results}:{start_index}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            logger.info(f"Google Books search cache HIT for query: {query}")
            return cached_result

        # Call API
        logger.info(f"Google Books search cache MISS for query: {query}")
        
        params = {
            "q": query,
            "maxResults": max_results,
            "startIndex": start_index,
        }
        
        if self.api_key:
            params["key"] = self.api_key

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/volumes",
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()

            # Cache result
            cache_service.set(cache_key, data)
            
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"Google Books API error: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Google Books API connection error: {e}")
            raise

    async def get_details(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        Get book details by Google Books ID.
        
        Args:
            book_id: Google Books volume ID
            
        Returns:
            Book details dictionary or None if not found
        """
        # Check cache
        cache_key = f"google_books:details:{book_id}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            logger.info(f"Google Books details cache HIT for ID: {book_id}")
            return cached_result

        # Call API
        logger.info(f"Google Books details cache MISS for ID: {book_id}")
        
        params = {}
        if self.api_key:
            params["key"] = self.api_key

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/volumes/{book_id}",
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()

            # Cache result (TTL 7 dias para detalhes específicos)
            cache_service.set(cache_key, data, ttl=604800)
            
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info(f"Book not found in Google Books API: {book_id}")
                return None
            logger.error(f"Google Books API error for ID {book_id}: {e}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"Google Books API connection error for ID {book_id}: {e}")
            raise

    def parse_book_data(self, volume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Google Books API response to simplified format.
        
        Args:
            volume_data: Raw volume data from API
            
        Returns:
            Simplified book data
        """
        volume_info = volume_data.get("volumeInfo", {})
        
        # Extract ISBNs
        isbn_10 = None
        isbn_13 = None
        for identifier in volume_info.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_10":
                isbn_10 = identifier.get("identifier")
            elif identifier.get("type") == "ISBN_13":
                isbn_13 = identifier.get("identifier")

        return {
            "google_books_id": volume_data.get("id"),
            "title": volume_info.get("title"),
            "authors": ", ".join(volume_info.get("authors", [])),
            "publisher": volume_info.get("publisher"),
            "published_date": volume_info.get("publishedDate"),
            "description": volume_info.get("description"),
            "isbn_10": isbn_10,
            "isbn_13": isbn_13,
            "page_count": volume_info.get("pageCount"),
            "categories": ", ".join(volume_info.get("categories", [])),
            "language": volume_info.get("language"),
            "image_url": volume_info.get("imageLinks", {}).get("thumbnail"),
            "preview_link": volume_info.get("previewLink"),
        }


# Singleton instance
google_books_service = GoogleBooksService()
