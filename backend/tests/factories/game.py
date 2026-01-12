import factory
from faker import Faker

from app.models.game import Game

fake = Faker()


class GameFactory(factory.Factory):
    """Factory for creating Game instances."""

    class Meta:
        model = Game

    id = factory.Sequence(lambda n: n + 1)
    rawg_id = factory.Sequence(lambda n: n + 1000)
    name = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3)[:-1])
    slug = factory.LazyAttribute(lambda o: o.name.lower().replace(" ", "-"))
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=500))
    released = factory.LazyAttribute(lambda _: str(fake.date_this_decade()))
    rating = factory.LazyAttribute(lambda _: round(fake.random.uniform(3.0, 5.0), 2))
    ratings_count = factory.LazyAttribute(lambda _: fake.random_int(min=100, max=10000))
    metacritic = factory.LazyAttribute(lambda _: fake.random_int(min=60, max=100))
    playtime = factory.LazyAttribute(lambda _: fake.random_int(min=5, max=100))
    genres = "Action,Adventure,RPG"
    tags = "Fantasy,Story Rich,Magic"
    platforms = "PC,PlayStation,Xbox"
    developers = factory.LazyAttribute(lambda _: fake.company())
    publishers = factory.LazyAttribute(lambda _: fake.company())
    image_url = factory.LazyAttribute(lambda _: fake.image_url())
    website = factory.LazyAttribute(lambda _: fake.url())
    created_at = factory.LazyFunction(fake.date_time_this_year)
    updated_at = factory.LazyFunction(fake.date_time_this_year)
