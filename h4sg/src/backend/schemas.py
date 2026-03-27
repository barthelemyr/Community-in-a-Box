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


class ShelfSimpleResponse(BaseModel):
    id: str
    name: str


class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str | None
    publisher: str | None

    model_config = ConfigDict(from_attributes=True)


class BookWithShelvesResponse(BaseModel):
    isbn: str
    title: str
    author: str | None
    publisher: str | None
    shelves: list[ShelfSimpleResponse]