import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, set_request_id

logger = get_logger()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers (helmet-like functionality).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request/response logging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Set request ID
        request_id = request.headers.get("X-Request-ID") or set_request_id()
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.bind(
            type="request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        ).info("Request started")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log response
            logger.bind(
                type="response",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            ).info("Request completed")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            logger.bind(
                type="error",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(e),
            ).error(f"Request failed: {str(e)}")
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for basic metrics tracking (in-memory).
    """

    def __init__(self, app):
        super().__init__(app)
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "total_duration_ms": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Update metrics
        self.metrics["requests_total"] += 1
        status_code = response.status_code
        self.metrics["requests_by_status"][status_code] = (
            self.metrics["requests_by_status"].get(status_code, 0) + 1
        )
        self.metrics["total_duration_ms"] += duration_ms
        
        return response

    def get_metrics(self):
        """Get current metrics."""
        avg_response_time = (
            self.metrics["total_duration_ms"] / self.metrics["requests_total"]
            if self.metrics["requests_total"] > 0
            else 0
        )
        
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (
            self.metrics["cache_hits"] / cache_total if cache_total > 0 else 0
        )
        
        return {
            **self.metrics,
            "avg_response_time_ms": round(avg_response_time, 2),
            "cache_hit_rate": round(cache_hit_rate, 2),
        }
