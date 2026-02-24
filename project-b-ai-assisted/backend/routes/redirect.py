from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from database import get_connection

router = APIRouter(tags=["redirect"])


@router.get("/{short_code}")
def redirect_to_url(short_code: str):
    if short_code in ("health", "docs", "openapi.json", "api"):
        raise HTTPException(status_code=404)

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Short code not found")

    conn.execute(
        "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
        (short_code,),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url=row["original_url"], status_code=307)
