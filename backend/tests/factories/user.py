import factory
from faker import Faker

from app.core.security import get_password_hash
from app.models.user import User

fake = Faker()


class UserFactory(factory.Factory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda _: fake.email().lower())
    hashed_password = factory.LazyAttribute(lambda _: get_password_hash("password123"))
    full_name = factory.LazyAttribute(lambda _: fake.name())
    is_active = True
    is_superuser = False
    created_at = factory.LazyFunction(fake.date_time_this_year)
    updated_at = factory.LazyFunction(fake.date_time_this_year)
