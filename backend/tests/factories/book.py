import factory
from faker import Faker

from app.models.book import Book

fake = Faker()


class BookFactory(factory.Factory):
    """Factory for creating Book instances."""

    class Meta:
        model = Book

    id = factory.Sequence(lambda n: n + 1)
    google_books_id = factory.LazyAttribute(lambda _: fake.uuid4())
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4)[:-1])
    authors = factory.LazyAttribute(lambda _: fake.name())
    publisher = factory.LazyAttribute(lambda _: fake.company())
    published_date = factory.LazyAttribute(lambda _: str(fake.year()))
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=500))
    isbn_10 = factory.LazyAttribute(lambda _: fake.isbn10())
    isbn_13 = factory.LazyAttribute(lambda _: fake.isbn13())
    page_count = factory.LazyAttribute(lambda _: fake.random_int(min=100, max=1000))
    categories = "Fiction,Adventure"
    language = "en"
    image_url = factory.LazyAttribute(lambda _: fake.image_url())
    preview_link = factory.LazyAttribute(lambda _: fake.url())
    created_at = factory.LazyFunction(fake.date_time_this_year)
    updated_at = factory.LazyFunction(fake.date_time_this_year)
