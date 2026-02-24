from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes.notes import router as notes_router


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(title="Notes API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(notes_router)


@app.get("/health")
def health():
    return {"status": "ok"}
