from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Shelf(Base):
    __tablename__ = "shelves"

    id: Mapped[str] = mapped_column(
        String(16),
        primary_key=True,
        index=True,
        server_default=text("lower(hex(randomblob(8)))"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    shelf_books: Mapped[list["ShelfBook"]] = relationship(
        back_populates="shelf",
        cascade="all, delete-orphan",
    )


class Book(Base):
    __tablename__ = "books"

    isbn: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String, nullable=True)

    shelf_books: Mapped[list["ShelfBook"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
    )


class ShelfBook(Base):
    __tablename__ = "shelves_books"

    shelf_id: Mapped[str] = mapped_column(
        ForeignKey("shelves.id", ondelete="CASCADE"),
        primary_key=True,
    )
    isbn: Mapped[str] = mapped_column(
        ForeignKey("books.isbn", ondelete="CASCADE"),
        primary_key=True,
    )
    last_scanned: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    shelf: Mapped["Shelf"] = relationship(back_populates="shelf_books")
    book: Mapped["Book"] = relationship(back_populates="shelf_books")