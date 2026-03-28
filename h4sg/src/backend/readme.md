README
# Installation (Windows cmd)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

# Run the server
```
fastapi dev
```

# Initialize database
```
sqlite3 .\library.db
.read insert.sql
.quit
```