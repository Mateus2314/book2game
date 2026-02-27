import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Email validation regex - simple and effective
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Debug: handle bytes
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode('utf-8')
    if isinstance(hashed_password, bytes):
        hashed_password = hashed_password.decode('utf-8')
    
    # Truncate if needed (bcrypt has 72 byte limit, not character limit)
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        # Reconstruct from bytes to avoid splitting multibyte characters
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Debug: check password length
    if isinstance(password, bytes):
        password = password.decode('utf-8')
    # Truncate if needed (bcrypt has 72 byte limit, not character limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Reconstruct from bytes to avoid splitting multibyte characters
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    if not email or not isinstance(email, str):
        return False
    # Check for consecutive dots which are invalid
    if ".." in email:
        return False
    # Check basic format
    if not EMAIL_REGEX.match(email):
        return False
    # Additional validation: no dot at start/end of local or domain parts
    if "@" in email:
        local, domain = email.split("@", 1)
        if local.startswith(".") or local.endswith("."):
            return False
        if domain.startswith(".") or domain.endswith("."):
            return False
    return True


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": str(uuid.uuid4())  # Unique token identifier
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token with unique identifier."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4())  # Unique token identifier
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        # Log the specific JWT error for debugging
        from app.core.logging import get_logger
        logger = get_logger()
        logger.warning(f"JWT decode failed: {type(e).__name__}: {str(e)}", extra={"request_id": ""})
        return None
