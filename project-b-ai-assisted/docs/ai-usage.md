# AI Usage Log

## Model Used

Claude Opus 4.6 via Claude Code CLI

## Why This Model

Opus is the most capable model in the Claude family for code generation. I used it through the Claude Code CLI which gives it direct access to the filesystem, git, and terminal. This made the workflow fast since it could read existing code, write files, run tests, and commit without me copying anything back and forth.

## How AI Was Used

- Generated the backend structure (main.py, database.py, models.py, auth.py, routes)
- Wrote all test cases
- Built the frontend page and styles
- Ran tests and fixed failures (route ordering bug with redirect catching /health)
- Made git commits with descriptive messages

## What I Did

- Defined the requirements and architecture
- Reviewed all generated code before committing
- Directed the implementation order and commit strategy
- Chose the design patterns (reused Project A's architecture)
- Found and provided the UI template reference
