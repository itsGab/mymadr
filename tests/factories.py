import factory

from mymadr.models import Book


class BookFactory(factory.Factory):  # type: ignore
    class Meta:  # type: ignore
        model = Book

    title = factory.Sequence(lambda n: f"Livro {n}")  # type: ignore
    year = 2025
    novelist_id = 1
