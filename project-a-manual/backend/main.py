from fastapi import FastAPI

from database import init_db
from routes.notes import router as notes_router

app = FastAPI(title="Notes API", version="0.1.0")
app.include_router(notes_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
