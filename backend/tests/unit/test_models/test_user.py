import pytest

from app.core.security import get_password_hash
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserUpdate
from tests.factories import UserFactory


@pytest.mark.unit
class TestUserCRUD:
    """Test user CRUD operations."""

    def test_create_user(self, db):
        """Test creating a new user."""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            full_name="Test User",
        )
        
        user = crud_user.create_user(db, user_data)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.hashed_password != "password123"
        assert user.is_active is True

    def test_get_user_by_id(self, db):
        """Test getting user by ID."""
        # Create user using factory
        created_user = UserFactory.build()
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        
        # Get user
        user = crud_user.get_user(db, created_user.id)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email

    def test_get_user_by_email(self, db):
        """Test getting user by email."""
        email = "unique@example.com"
        user_data = UserCreate(email=email, password="password123")
        
        created_user = crud_user.create_user(db, user_data)
        
        # Get user by email
        user = crud_user.get_user_by_email(db, email)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.email == email.lower()

    def test_get_user_by_email_case_insensitive(self, db):
        """Test email is case-insensitive."""
        user_data = UserCreate(email="Test@Example.COM", password="password123")
        
        created_user = crud_user.create_user(db, user_data)
        
        # Get with different case
        user = crud_user.get_user_by_email(db, "test@example.com")
        
        assert user is not None
        assert user.id == created_user.id

    def test_update_user(self, db):
        """Test updating user."""
        user_data = UserCreate(email="test@example.com", password="password123")
        user = crud_user.create_user(db, user_data)
        
        # Update user
        update_data = UserUpdate(full_name="Updated Name")
        updated_user = crud_user.update_user(db, user, update_data)
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "test@example.com"

    def test_authenticate_user_success(self, db):
        """Test successful user authentication."""
        email = "auth@example.com"
        password = "password123"
        user_data = UserCreate(email=email, password=password)
        
        crud_user.create_user(db, user_data)
        
        # Authenticate
        user = crud_user.authenticate_user(db, email, password)
        
        assert user is not None
        assert user.email == email.lower()

    def test_authenticate_user_wrong_password(self, db):
        """Test authentication with wrong password."""
        email = "auth@example.com"
        password = "password123"
        user_data = UserCreate(email=email, password=password)
        
        crud_user.create_user(db, user_data)
        
        # Try with wrong password
        user = crud_user.authenticate_user(db, email, "wrongpassword")
        
        assert user is None

    def test_authenticate_user_not_found(self, db):
        """Test authentication with non-existent user."""
        user = crud_user.authenticate_user(db, "notfound@example.com", "password")
        
        assert user is None

    def test_is_active(self, db):
        """Test checking if user is active."""
        user = UserFactory.build(is_active=True)
        
        assert crud_user.is_active(user) is True
        
        user.is_active = False
        assert crud_user.is_active(user) is False
