# Backend Developer Test

Two small projects built for a backend developer technical challenge.

## Project A: Notes API (Manual)

A notes app with CRUD, search by tag/keyword, and API key auth. Built without AI tools.

- **Backend:** FastAPI, SQLite, Pydantic validation
- **Frontend:** Next.js + React
- **Tests:** 12 pytest tests covering CRUD, search, auth, validation

I went with raw sqlite3 instead of an ORM since there's only one table. Tags are stored as JSON in a TEXT column. Search uses LIKE queries. Auth is a static API key checked via a FastAPI dependency on the router.

See `project-a-manual/docs/` for planning notes and setup instructions.

## Project B: URL Shortener (AI-Assisted)

A URL shortener that generates short codes, redirects visitors, and tracks click counts. Built with Claude Opus 4.6 via Claude Code CLI.

- **Backend:** FastAPI, SQLite, Pydantic with URL validation
- **Frontend:** Next.js + React
- **Tests:** 16 pytest tests covering create, redirect, stats, duplicates, auth

Reused the same architecture from Project A. The main challenge was route ordering since `GET /{short_code}` is a catch-all that can intercept other endpoints. Solved by registering specific routes before the redirect router.

See `project-b-ai-assisted/docs/` for planning notes, setup instructions, and AI usage details.
See `project-b-ai-assisted/prompts/` for the session transcript.

## Running either project

Both projects follow the same pattern:

```bash
# backend
cd project-{a-manual,b-ai-assisted}/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# frontend (separate terminal)
cd project-{a-manual,b-ai-assisted}/frontend
npm install
npm run dev
```

## Running tests

```bash
cd project-{a-manual,b-ai-assisted}
source backend/venv/bin/activate
pytest tests/ -v
```
