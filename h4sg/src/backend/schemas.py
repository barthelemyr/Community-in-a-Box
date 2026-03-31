from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShelfCreate(BaseModel):
    name: str
    latitude: float
    longitude: float


class ShelfResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str | None
    publisher: str | None

    model_config = ConfigDict(from_attributes=True)


class ShelfBookResponse(BaseModel):
    isbn: str
    title: str
    author: str | None
    publisher: str | None
    last_scanned: datetime

    model_config = ConfigDict(from_attributes=True)


class ShelfWithBooksResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    books: list[ShelfBookResponse]

    model_config = ConfigDict(from_attributes=True)


class ShelfBooksGroupResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    last_scanned: datetime

    model_config = ConfigDict(from_attributes=True)