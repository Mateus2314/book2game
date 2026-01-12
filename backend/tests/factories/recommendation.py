import json

import factory
from faker import Faker

from app.models.recommendation import Recommendation

fake = Faker()


class RecommendationFactory(factory.Factory):
    """Factory for creating Recommendation instances."""

    class Meta:
        model = Recommendation

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    book_id = factory.Sequence(lambda n: n + 1)
    games = factory.LazyAttribute(
        lambda _: json.dumps([
            {"game_id": fake.random_int(min=1, max=100), "score": round(fake.random.uniform(0.7, 1.0), 2)},
            {"game_id": fake.random_int(min=1, max=100), "score": round(fake.random.uniform(0.7, 1.0), 2)},
            {"game_id": fake.random_int(min=1, max=100), "score": round(fake.random.uniform(0.7, 1.0), 2)},
        ])
    )
    ai_generated = True
    similarity_score = factory.LazyAttribute(lambda _: round(fake.random.uniform(0.7, 1.0), 2))
    processing_time_ms = factory.LazyAttribute(lambda _: fake.random_int(min=500, max=5000))
    created_at = factory.LazyFunction(fake.date_time_this_year)
    updated_at = factory.LazyFunction(fake.date_time_this_year)
