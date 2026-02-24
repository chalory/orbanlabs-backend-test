import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from database import get_connection
from models import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/api/notes", tags=["notes"])


def row_to_note(row) -> NoteResponse:
    return NoteResponse(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        tags=json.loads(row["tags"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(note: NoteCreate):
    conn = get_connection()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        "INSERT INTO notes (title, body, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (note.title, note.body, json.dumps(note.tags), now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return row_to_note(row)


@router.get("", response_model=list[NoteResponse])
def list_notes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notes ORDER BY created_at DESC").fetchall()
    conn.close()
    return [row_to_note(r) for r in rows]


@router.get("/search", response_model=list[NoteResponse])
def search_notes(
    tag: str | None = Query(default=None),
    q: str | None = Query(default=None),
):
    conn = get_connection()
    clauses = []
    params = []

    if tag:
        clauses.append("tags LIKE ?")
        params.append(f'%"{tag}"%')
    if q:
        clauses.append("(title LIKE ? OR body LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])

    where = " AND ".join(clauses) if clauses else "1=1"
    rows = conn.execute(
        f"SELECT * FROM notes WHERE {where} ORDER BY created_at DESC", params
    ).fetchall()
    conn.close()
    return [row_to_note(r) for r in rows]


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return row_to_note(row)


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, updates: NoteUpdate):
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")

    fields = {}
    if updates.title is not None:
        fields["title"] = updates.title
    if updates.body is not None:
        fields["body"] = updates.body
    if updates.tags is not None:
        fields["tags"] = json.dumps(updates.tags)

    if not fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    fields["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [note_id]

    conn.execute(f"UPDATE notes SET {set_clause} WHERE id = ?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    return row_to_note(row)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
