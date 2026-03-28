from datetime import datetime, timezone

import requests
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
import secrets

from database import Base, SessionLocal, engine
from models import Book, Shelf, ShelfBook
from schemas import (
    BookResponse,
    ShelfBookResponse,
    ShelfBooksGroupResponse,
    ShelfCreate,
    ShelfResponse,
    ShelfWithBooksResponse,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def normalize_isbn(isbn: str) -> str:
    """Normalize an ISBN by removing spaces and hyphens."""
    return isbn.replace("-", "").replace(" ", "").strip()


def fetch_book_from_openlibrary(isbn: str) -> dict | None:
    """Fetch book metadata from Open Library using the given ISBN."""
    normalized_isbn = normalize_isbn(isbn)
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{normalized_isbn}&format=json&jscmd=data"

    response = requests.get(
        url,
        headers={
            "User-Agent": "book-shelf-tracker/1.0"
        },
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    book_data = data.get(f"ISBN:{normalized_isbn}")

    if book_data is None:
        return None

    authors = ", ".join(
        author["name"]
        for author in book_data.get("authors", [])
        if author.get("name")
    ) or None

    publishers = ", ".join(
        publisher["name"]
        for publisher in book_data.get("publishers", [])
        if publisher.get("name")
    ) or None

    title = book_data.get("title")
    if not title:
        return None

    return {
        "isbn": normalized_isbn,
        "title": title,
        "author": authors,
        "publisher": publishers,
    }


def build_book_response(book: Book) -> BookResponse:
    """Convert a Book model into the public book response schema."""
    return BookResponse(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
    )


def build_shelf_book_response(book: Book, last_scanned: datetime) -> ShelfBookResponse:
    """Convert a Book model plus shelf scan timestamp into a shelf book response."""
    return ShelfBookResponse(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        last_scanned=last_scanned,
    )


@app.get("/")
def read_root():
    """Health check endpoint to verify that the backend is running."""
    return {"message": "Backend is running"}


@app.post("/shelves", response_model=ShelfResponse)
def create_shelf(shelf_data: ShelfCreate, db: Session = Depends(get_db)):
    """Create a new shelf with name and coordinates."""
    existing_shelf = db.scalar(
        select(Shelf).where(Shelf.name == shelf_data.name)
    )
    if existing_shelf is not None:
        raise HTTPException(status_code=400, detail="Shelf name already exists")

    shelf = Shelf(
        id=secrets.token_hex(8),
        name=shelf_data.name,
        latitude=shelf_data.latitude,
        longitude=shelf_data.longitude,
    )
    db.add(shelf)
    db.commit()
    db.refresh(shelf)
    return shelf


@app.get("/shelves", response_model=list[ShelfResponse])
def list_shelves(db: Session = Depends(get_db)):
    """Return all shelves stored in the database."""
    shelves = db.scalars(select(Shelf)).all()
    return shelves


@app.get("/shelves/books", response_model=list[ShelfWithBooksResponse])
def list_books_grouped_by_shelves(db: Session = Depends(get_db)):
    """Return all shelves with their assigned books grouped under each shelf."""
    shelves = db.scalars(select(Shelf).order_by(Shelf.name)).all()

    shelf_books = db.scalars(
        select(ShelfBook)
        .join(Book, Book.isbn == ShelfBook.isbn)
        .order_by(ShelfBook.shelf_id, Book.title, Book.isbn)
    ).all()

    books_by_shelf: dict[str, list[ShelfBookResponse]] = {shelf.id: [] for shelf in shelves}
    books_by_isbn: dict[str, Book] = {
        book.isbn: book for book in db.scalars(select(Book)).all()
    }

    for shelf_book in shelf_books:
        book = books_by_isbn.get(shelf_book.isbn)
        if book is None:
            continue

        books_by_shelf[shelf_book.shelf_id].append(
            build_shelf_book_response(book, shelf_book.last_scanned)
        )

    return [
        ShelfWithBooksResponse(
            id=shelf.id,
            name=shelf.name,
            latitude=shelf.latitude,
            longitude=shelf.longitude,
            books=books_by_shelf.get(shelf.id, []),
        )
        for shelf in shelves
    ]


@app.get("/shelves/books/{isbn}", response_model=list[ShelfBooksGroupResponse])
def list_shelf_occurrences_for_book(isbn: str, db: Session = Depends(get_db)):
    """Return all shelves that currently contain the given ISBN."""
    normalized_isbn = normalize_isbn(isbn)

    shelf_books = db.scalars(
        select(ShelfBook)
        .where(ShelfBook.isbn == normalized_isbn)
        .order_by(ShelfBook.shelf_id)
    ).all()

    if not shelf_books:
        return []

    shelves_by_id: dict[str, Shelf] = {
        shelf.id: shelf for shelf in db.scalars(select(Shelf)).all()
    }

    result: list[ShelfBooksGroupResponse] = []
    for shelf_book in shelf_books:
        shelf = shelves_by_id.get(shelf_book.shelf_id)
        if shelf is None:
            continue

        result.append(
            ShelfBooksGroupResponse(
                id=shelf.id,
                name=shelf.name,
                latitude=shelf.latitude,
                longitude=shelf.longitude,
                last_scanned=shelf_book.last_scanned,
            )
        )

    return result


@app.get("/shelves/{shelf_id}", response_model=ShelfResponse)
def get_shelf_by_id(shelf_id: str, db: Session = Depends(get_db)):
    """Return one shelf by its shelf ID."""
    shelf = db.get(Shelf, shelf_id)
    if shelf is None:
        raise HTTPException(status_code=404, detail="Shelf not found")

    return shelf


@app.get("/books", response_model=list[BookResponse])
def list_books(db: Session = Depends(get_db)):
    """Return all books stored in the books table."""
    books = db.scalars(
        select(Book).order_by(Book.title, Book.isbn)
    ).all()

    return [build_book_response(book) for book in books]


@app.get("/books/{isbn}", response_model=BookResponse)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    """Return one book by its ISBN without shelf association data."""
    normalized_isbn = normalize_isbn(isbn)

    book = db.get(Book, normalized_isbn)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return build_book_response(book)


@app.get("/shelves/{shelf_id}/books", response_model=list[ShelfBookResponse])
def list_books_for_shelf(shelf_id: str, db: Session = Depends(get_db)):
    """Return all books currently assigned to a specific shelf."""
    shelf = db.get(Shelf, shelf_id)
    if shelf is None:
        raise HTTPException(status_code=404, detail="Shelf not found")

    shelf_books = db.scalars(
        select(ShelfBook)
        .where(ShelfBook.shelf_id == shelf_id)
        .order_by(ShelfBook.last_scanned.desc())
    ).all()

    if not shelf_books:
        return []

    books_by_isbn: dict[str, Book] = {
        book.isbn: book
        for book in db.scalars(
            select(Book).where(Book.isbn.in_([shelf_book.isbn for shelf_book in shelf_books]))
        ).all()
    }

    return [
        build_shelf_book_response(books_by_isbn[shelf_book.isbn], shelf_book.last_scanned)
        for shelf_book in shelf_books
        if shelf_book.isbn in books_by_isbn
    ]


@app.put("/shelves/{shelf_id}/books/{isbn}", response_model=ShelfBookResponse)
def add_or_update_book_in_shelf(
    shelf_id: str,
    isbn: str,
    response: Response,
    db: Session = Depends(get_db),
):
    """Add a book to a shelf or update its last_scanned timestamp if it already exists there."""
    normalized_isbn = normalize_isbn(isbn)
    scanned_at = datetime.now(timezone.utc)

    shelf = db.get(Shelf, shelf_id)
    if shelf is None:
        raise HTTPException(status_code=404, detail="Shelf not found")

    book = db.get(Book, normalized_isbn)
    if book is None:
        try:
            openlibrary_book = fetch_book_from_openlibrary(normalized_isbn)
        except requests.RequestException:
            raise HTTPException(
                status_code=502,
                detail="Could not fetch book data from Open Library",
            )

        if openlibrary_book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        book = Book(
            isbn=openlibrary_book["isbn"],
            title=openlibrary_book["title"],
            author=openlibrary_book["author"],
            publisher=openlibrary_book["publisher"],
        )
        db.add(book)
        db.flush()

    shelf_book = db.get(ShelfBook, (shelf_id, normalized_isbn))

    if shelf_book is None:
        shelf_book = ShelfBook(
            shelf_id=shelf_id,
            isbn=normalized_isbn,
            last_scanned=scanned_at,
        )
        db.add(shelf_book)
        response.status_code = status.HTTP_201_CREATED
    else:
        shelf_book.last_scanned = scanned_at
        response.status_code = status.HTTP_200_OK

    db.commit()
    db.refresh(book)
    db.refresh(shelf_book)

    return build_shelf_book_response(book, shelf_book.last_scanned)


@app.delete("/shelves/{shelf_id}/books/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def borrow_book_from_shelf(shelf_id: str, isbn: str, db: Session = Depends(get_db)):
    """Remove a book from a shelf, for example when it is borrowed."""
    normalized_isbn = normalize_isbn(isbn)

    shelf = db.get(Shelf, shelf_id)
    if shelf is None:
        raise HTTPException(status_code=404, detail="Shelf not found")

    shelf_book = db.get(ShelfBook, (shelf_id, normalized_isbn))
    if shelf_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book is not assigned to this shelf",
        )

    db.delete(shelf_book)
    db.commit()