from pydantic import BaseModel, Field
from typing import Optional


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = ""
    tags: list[str] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    body: Optional[str] = None
    tags: Optional[list[str]] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    body: str
    tags: list[str]
    created_at: str
    updated_at: str
