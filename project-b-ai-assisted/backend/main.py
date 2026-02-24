from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes.links import router as links_router
from routes.redirect import router as redirect_router


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(title="URL Shortener", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(links_router)
app.include_router(redirect_router)


@app.get("/health")
def health():
    return {"status": "ok"}
