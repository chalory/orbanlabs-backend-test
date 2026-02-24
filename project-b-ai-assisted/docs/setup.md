# Setup

## What you need

- Python 3.11+
- Node.js 18+

## Backend

```bash
cd project-b-ai-assisted/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API runs on `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

Default API key is `dev-api-key`. Set `API_KEY` env var to change it.

### Quick test

```bash
# shorten a url
curl -X POST http://localhost:8000/api/links \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{"original_url": "https://example.com/very/long/url"}'

# list your links
curl http://localhost:8000/api/links -H "X-API-Key: dev-api-key"

# check stats
curl http://localhost:8000/api/links/ABC123/stats -H "X-API-Key: dev-api-key"

# test redirect (replace ABC123 with your actual code)
curl -L http://localhost:8000/ABC123
```

## Tests

```bash
cd project-b-ai-assisted
source backend/venv/bin/activate
pytest tests/ -v
```

## Frontend

```bash
cd project-b-ai-assisted/frontend
npm install
npm run dev
```

Runs on `http://localhost:3000`.
