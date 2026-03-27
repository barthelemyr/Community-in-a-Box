from datetime import datetime, timezone

import requests
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import Base, SessionLocal, engine
from models import Book, Shelf, ShelfBook
from schemas import (
    BookResponse,
    BookWithShelvesResponse,
    ShelfCreate,
    ShelfResponse,
    ShelfSimpleResponse,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_isbn(isbn: str) -> str:
    return isbn.replace("-", "").replace(" ", "").strip()


def fetch_book_from_openlibrary(isbn: str) -> dict | None:
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


def build_book_with_shelves_response(book: Book) -> BookWithShelvesResponse:
    shelves = [
        ShelfSimpleResponse(
            id=shelf_book.shelf.id,
            name=shelf_book.shelf.name,
        )
        for shelf_book in book.shelf_books
    ]

    return BookWithShelvesResponse(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        shelves=shelves,
    )


@app.get("/")
def read_root():
    return {"message": "Backend is running"}


@app.post("/shelves", response_model=ShelfResponse)
def create_shelf(shelf_data: ShelfCreate, db: Session = Depends(get_db)):
    existing_shelf = db.scalar(
        select(Shelf).where(Shelf.name == shelf_data.name)
    )
    if existing_shelf is not None:
        raise HTTPException(status_code=400, detail="Shelf name already exists")

    shelf = Shelf(
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
    shelves = db.scalars(select(Shelf)).all()
    return shelves

@app.get("/shelves/{shelf_id}", response_model=ShelfResponse)
def get_shelf_by_id(shelf_id: str, db: Session = Depends(get_db)):
    shelf = db.get(Shelf, shelf_id)
    if shelf is None:
        raise HTTPException(status_code=404, detail="Shelf not found")

    return shelf

@app.get("/books", response_model=list[BookWithShelvesResponse])
def list_books(db: Session = Depends(get_db)):
    books = db.scalars(
        select(Book).options(
            selectinload(Book.shelf_books).selectinload(ShelfBook.shelf)
        )
    ).all()

    return [build_book_with_shelves_response(book) for book in books]


@app.get("/books/{isbn}", response_model=BookWithShelvesResponse)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    normalized_isbn = normalize_isbn(isbn)

    book = db.scalar(
        select(Book)
        .where(Book.isbn == normalized_isbn)
        .options(
            selectinload(Book.shelf_books).selectinload(ShelfBook.shelf)
        )
    )

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return build_book_with_shelves_response(book)


@app.get("/shelves/{shelf_id}/books", response_model=list[BookResponse])
def list_books_for_shelf(shelf_id: int, db: Session = Depends(get_db)):
    shelf = db.get(Shelf, shelf_id)
    if shelf is None:
        raise HTTPException(status_code=404, detail="Shelf not found")

    books = db.scalars(
        select(Book)
        .join(ShelfBook, ShelfBook.isbn == Book.isbn)
        .where(ShelfBook.shelf_id == shelf_id)
    ).all()

    return books


@app.put("/shelves/{shelf_id}/books/{isbn}", response_model=BookResponse)
def add_or_update_book_in_shelf(
    shelf_id: int,
    isbn: str,
    response: Response,
    db: Session = Depends(get_db),
):
    normalized_isbn = normalize_isbn(isbn)

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
            last_scanned=datetime.now(timezone.utc),
        )
        db.add(shelf_book)
        response.status_code = status.HTTP_201_CREATED
    else:
        shelf_book.last_scanned = datetime.now(timezone.utc)
        response.status_code = status.HTTP_200_OK

    db.commit()
    db.refresh(book)
    return book


@app.delete("/shelves/{shelf_id}/books/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def borrow_book_from_shelf(shelf_id: int, isbn: str, db: Session = Depends(get_db)):
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