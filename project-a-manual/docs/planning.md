# Planning Notes

## What I'm building

CRUD notes app. Users create/read/update/delete notes, each with a title, body, and tags. There's a search endpoint and API key auth. SQLite for storage, FastAPI for the API.

## Why SQLite

Didn't want to drag in Postgres for something this small. SQLite is zero-config and works fine for a single-user API. Tags are stored as JSON in a TEXT column. It's not normalized but the search requirement is just "filter by tag", and LIKE on a JSON string handles that.

## Why not SQLAlchemy

One table. Didn't need an ORM for this. Raw sqlite3 with Row factory is enough and keeps the code short.

## Auth approach

Static API key read from an env var, checked via a FastAPI dependency on the router. I considered JWT but it's way more than what's needed here. The spec says "simple auth via API key" so that's what I did.

## Search

`/api/notes/search` takes `tag` and/or `q` params. Tag matching does a LIKE on the JSON string. Keyword search checks title and body. Both can combine. I put the search route before `/{note_id}` so FastAPI doesn't try to parse "search" as a note ID.

## What I'd do differently at scale

- Separate tags table with a many-to-many join
- Full-text search instead of LIKE
- Connection pooling
- Rate limiting on the auth layer
