import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict

from loguru import logger

from app.core.config import settings

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def setup_logging():
    """Setup structured logging with loguru."""
    # Remove default handler
    logger.remove()
    
    # Determine format and serialization based on settings
    if settings.LOG_FORMAT == "json":
        # JSON format for production - use Loguru's built-in serialization
        # No custom format needed when serialize=True
        log_format = "{time} {level} {message}"  # Placeholder (not used with serialize=True)
        use_serialize = True
    else:
        # Human-readable format for development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[request_id]}</cyan> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        use_serialize = False
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        serialize=use_serialize,
    )
    
    # Add file handler with rotation
    logger.add(
        "logs/app.log",
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        serialize=use_serialize,
        enqueue=True,
    )
    
    return logger


def get_logger():
    """Get logger with request ID context."""
    request_id = request_id_var.get()
    return logger.bind(request_id=request_id)


def set_request_id(request_id: str = None):
    """Set request ID in context."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


# Initialize logging
setup_logging()
