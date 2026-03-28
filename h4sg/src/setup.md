# Setup

## Backend

Prerequisites: python and sqlite3 installed
### Installation (Windows cmd)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Initialize database
```
sqlite3 .\library.db
.read insert.sql
.quit
```

#### Run the server
```
fastapi dev
```

### Backend Documentation

#### Purpose

This backend provides a REST API for managing public book-sharing shelves.  
Its purpose is to keep track of which books are currently located in which shelf.

Books are identified by their ISBN. When a book is added to a shelf, the backend first checks whether the book already exists in the local database. If not, it fetches the book metadata from the Open Library API and stores it locally.

#### Main Features

- create and list shelves
- create book-to-shelf associations by ISBN
- remove books from shelves when they are borrowed
- list all books stored in the system
- list all books inside a specific shelf
- list all shelves with their grouped books
- check in which shelves a specific ISBN is currently present

#### Technologies Used

#### FastAPI
FastAPI is used to implement the REST API.  
It provides clear route definitions, request/response validation, and automatic API documentation.

#### SQLite
SQLite is used as the local database.  
It is lightweight, easy to set up, and well suited for a prototype or a small backend project.

#### Open Library API
The Open Library API is used to fetch book metadata from an ISBN, especially:
- title
- author
- publisher

This avoids manual entry of book data and prevents unnecessary duplicate lookups.

#### Data Model

The backend currently uses three main tables:

- **shelves**: stores shelf information such as name and coordinates
- **books**: stores book metadata such as ISBN, title, author, and publisher
- **shelves_books**: stores the assignment of books to shelves and the `last_scanned` timestamp

#### Planned Spotin.ch Integration

At the moment, shelves are stored directly in the backend database.

A possible future improvement would be to load shelves dynamically from **spotin.ch** instead of maintaining them locally. In that case, the backend would mainly manage the book-to-shelf associations, while the shelf locations themselves would come from Spotin.

The main open design question is whether the system should become fully dependent on spotin.ch, or whether an internal shelf database should still be kept for reliability and independence.

Two possible approaches are:

- create shelves in this application first and then sync them to spotin.ch
- create shelves in spotin.ch first and let this backend detect and use them

## Frontend

Prerequisites: Node.js installed

### Installation
```bash
cd path/to/Community-in-a-box/src/frontend
npm install
```
Download the necessary dependencies

### Running
```bash
npm run dev
```
If the backend is running, this starts the webapp.