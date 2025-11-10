from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class Account:
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


@table_registry.mapped_as_dataclass
class Book:
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column()
    year: Mapped[int] = mapped_column()
    novelist_id: Mapped[int] = mapped_column(ForeignKey("novelists.id"))
    novelist: Mapped["Novelist"] = relationship(
        init=False,
        back_populates="books",
    )


@table_registry.mapped_as_dataclass
class Novelist:
    __tablename__ = "novelists"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    books: Mapped[list["Book"]] = relationship(
        init=False,
        back_populates="novelist",
        cascade="all, delete-orphan",
    )
