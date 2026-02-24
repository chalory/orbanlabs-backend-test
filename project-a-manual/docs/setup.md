# Setup

## What you need

- Python 3.11+
- Node.js 18+

## Backend

```bash
cd project-a-manual/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API runs on `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

By default the API key is `dev-api-key`. Change it by setting the `API_KEY` env var.

### Quick test

```bash
# create a note
curl -X POST http://localhost:8000/api/notes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{"title": "test", "body": "hello", "tags": ["demo"]}'

# list notes
curl http://localhost:8000/api/notes -H "X-API-Key: dev-api-key"

# search
curl "http://localhost:8000/api/notes/search?tag=demo" -H "X-API-Key: dev-api-key"
```

## Tests

```bash
cd project-a-manual
source backend/venv/bin/activate
pytest tests/ -v
```

## Frontend

```bash
cd project-a-manual/frontend
npm install
npm run dev
```

Runs on `http://localhost:3000`.
