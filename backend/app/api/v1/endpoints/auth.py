from fastapi import Form, APIRouter, Body, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, validate_email
from app.crud import user as crud_user
from app.schemas.user import Token, User as UserSchema , UserCreate

router = APIRouter()

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Strict rate limiting for registration
async def register(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user with email validation.
    Rate limited to 5 requests per minute to prevent abuse.
    """
    # Validate email format
    if not validate_email(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )
    
    # Check if user already exists
    existing_user = crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user = crud_user.create_user(db, user_in)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
    user_schema = UserSchema.model_validate(user)
    return Token(
        access_token=access_token, 
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_schema
        )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Strict rate limiting for login (anti-brute force)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    print("Login Backend :", email, password)
    """
    Login with email and password.
    Rate limited to 5 requests per minute to prevent brute force attacks.
    """
    # Validate email format
    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )
    
    # Authenticate user
    user = crud_user.authenticate_user(db, email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Create tokens (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
    user_schema = UserSchema.model_validate(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token, 
        token_type="bearer", 
        user=user_schema
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    Expects JSON body: {"refresh_token": "your_token"}
    """
    # Log token details for debugging
    from app.core.logging import get_logger
    logger = get_logger()
    logger.debug(
        f"Attempting to decode refresh token (length: {len(refresh_token)})",
        extra={"request_id": ""}
    )
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not decode refresh token - token may be expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type: expected 'refresh', got '{payload.get('type')}'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID (sub claim)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert user_id from string to int for database query
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid user ID format in token: {user_id_str}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists and is active
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with ID {user_id} not found",
        )
    
    if not crud_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    
    # Create new tokens (sub must be string per JWT spec)
    new_access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
    
    return Token(access_token=new_access_token, refresh_token=new_refresh_token)
