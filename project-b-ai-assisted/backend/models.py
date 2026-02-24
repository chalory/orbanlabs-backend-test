import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class LinkCreate(BaseModel):
    original_url: str = Field(min_length=5, max_length=2000)
    custom_code: Optional[str] = Field(default=None, min_length=3, max_length=20)

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v):
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(pattern, v):
            raise ValueError("Invalid URL format")
        return v


class LinkResponse(BaseModel):
    id: int
    short_code: str
    original_url: str
    short_url: str
    click_count: int
    created_at: str
    updated_at: str


class LinkStats(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: str
