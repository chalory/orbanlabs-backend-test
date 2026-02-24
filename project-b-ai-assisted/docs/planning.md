# Planning Notes

## What this is

URL shortener. Takes a long URL, gives back a short code, redirects visitors, tracks clicks. Same stack as Project A: FastAPI + SQLite backend, Next.js frontend.

## Approach

Reused the same architecture from Project A since it worked well. One SQLite table for URLs with a click counter. Short codes are random 6-char alphanumeric strings. If someone submits a URL that already exists, return the existing short code instead of creating a duplicate.

## Redirect routing

The tricky part was the redirect endpoint. It's `GET /{short_code}` which is a catch-all. Had to make sure it doesn't intercept `/health`, `/docs`, or `/api/*`. Solved by registering the health endpoint before the redirect router so FastAPI matches it first.

## Auth

Same API key pattern as Project A. Creating and managing links requires auth. Redirects are public since anyone clicking a short link shouldn't need a key.

## What I'd change

- Add expiration dates for links
- Rate limiting on the create endpoint
- Analytics beyond just click count (referrer, timestamp, geo)
- Custom short code validation (no reserved words)
