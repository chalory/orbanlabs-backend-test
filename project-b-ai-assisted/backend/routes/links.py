import string
import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import verify_api_key
from database import get_connection
from models import LinkCreate, LinkResponse, LinkStats

router = APIRouter(prefix="/api/links", tags=["links"], dependencies=[Depends(verify_api_key)])


def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def make_short_url(request: Request, code: str) -> str:
    return f"{request.base_url}{code}"


def row_to_response(row, short_url: str) -> LinkResponse:
    return LinkResponse(
        id=row["id"],
        short_code=row["short_code"],
        original_url=row["original_url"],
        short_url=short_url,
        click_count=row["click_count"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("", response_model=LinkResponse, status_code=201)
def create_link(link: LinkCreate, request: Request):
    conn = get_connection()

    existing = conn.execute(
        "SELECT * FROM urls WHERE original_url = ?", (link.original_url,)
    ).fetchone()
    if existing:
        short_url = make_short_url(request, existing["short_code"])
        conn.close()
        return row_to_response(existing, short_url)

    code = link.custom_code or generate_code()

    if conn.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,)).fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Short code already taken")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        "INSERT INTO urls (short_code, original_url, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (code, link.original_url, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM urls WHERE id = ?", (cursor.lastrowid,)).fetchone()
    short_url = make_short_url(request, row["short_code"])
    conn.close()
    return row_to_response(row, short_url)


@router.get("", response_model=list[LinkResponse])
def list_links(request: Request):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM urls ORDER BY created_at DESC").fetchall()
    conn.close()
    return [row_to_response(r, make_short_url(request, r["short_code"])) for r in rows]


@router.get("/{short_code}/stats", response_model=LinkStats)
def get_stats(short_code: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Short code not found")
    return LinkStats(
        short_code=row["short_code"],
        original_url=row["original_url"],
        click_count=row["click_count"],
        created_at=row["created_at"],
    )


@router.delete("/{short_code}", status_code=204)
def delete_link(short_code: str):
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Short code not found")
    conn.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
    conn.commit()
    conn.close()
