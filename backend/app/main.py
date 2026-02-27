from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.middleware import LoggingMiddleware, MetricsMiddleware, SecurityHeadersMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Book2Game API",
    description="Sistema de recomendação de jogos baseados em livros usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiter (disabled in testing environment)
if not settings.TESTING:
    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

# Security headers (helmet-like)
app.add_middleware(SecurityHeadersMiddleware)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Metrics middleware
metrics_middleware = MetricsMiddleware(app)
app.add_middleware(MetricsMiddleware)
app.state.metrics = metrics_middleware

# CORS Configuration (must be last)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Book2Game API",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """Get application metrics."""
    if hasattr(app.state, "metrics"):
        return app.state.metrics.get_metrics()
    return {"error": "Metrics not available"}
