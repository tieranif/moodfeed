# MoodFeed

*MoodFeed* is a small FastAPI backend demonstrating posts and emoji reactions stored in Postgres.

Stack: Python, FastAPI, SQLAlchemy, PostgreSQL

Quick start

1. Install Postgres and create DB:

```bash
brew install postgresql@16
brew services start postgresql@16
createdb moodfeed
psql moodfeed  # verify
```

2. Create a venv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic
```

3. Configure DB URL in `backend/.env`:

```
DATABASE_URL=postgresql://localhost/moodfeed
```

4. Create tables (first run only):

Start the server once; `Base.metadata.create_all(bind=engine)` is enabled in `backend/main.py` for the initial run.

5. Run server:

```bash
cd backend
/path/to/.venv/bin/python -m uvicorn main:app --reload
# Open http://127.0.0.1:8001/docs
```

6. Publish

Use VS Code Source Control → Publish to GitHub (OAuth flow) to create the remote without a personal token.