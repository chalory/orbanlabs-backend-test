import os
from fastapi import Request, HTTPException

API_KEY = os.getenv("API_KEY", "dev-api-key")


async def verify_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
