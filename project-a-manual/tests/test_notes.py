import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app
from database import DB_PATH, init_db, get_connection

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-api-key"}


@pytest.fixture(autouse=True)
def clean_db():
    init_db()
    yield
    conn = get_connection()
    conn.execute("DELETE FROM notes")
    conn.commit()
    conn.close()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_note():
    r = client.post("/api/notes", json={"title": "Test", "body": "Body", "tags": ["a"]}, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Test"
    assert data["tags"] == ["a"]
    assert "id" in data


def test_list_notes():
    client.post("/api/notes", json={"title": "N1"}, headers=HEADERS)
    client.post("/api/notes", json={"title": "N2"}, headers=HEADERS)
    r = client.get("/api/notes", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_get_note():
    r = client.post("/api/notes", json={"title": "Find me"}, headers=HEADERS)
    note_id = r.json()["id"]
    r = client.get(f"/api/notes/{note_id}", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["title"] == "Find me"


def test_get_note_not_found():
    r = client.get("/api/notes/9999", headers=HEADERS)
    assert r.status_code == 404


def test_update_note():
    r = client.post("/api/notes", json={"title": "Old"}, headers=HEADERS)
    note_id = r.json()["id"]
    r = client.put(f"/api/notes/{note_id}", json={"title": "New"}, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["title"] == "New"


def test_delete_note():
    r = client.post("/api/notes", json={"title": "Gone"}, headers=HEADERS)
    note_id = r.json()["id"]
    r = client.delete(f"/api/notes/{note_id}", headers=HEADERS)
    assert r.status_code == 204
    r = client.get(f"/api/notes/{note_id}", headers=HEADERS)
    assert r.status_code == 404


def test_search_by_tag():
    client.post("/api/notes", json={"title": "Tagged", "tags": ["python"]}, headers=HEADERS)
    r = client.get("/api/notes/search?tag=python", headers=HEADERS)
    assert r.status_code == 200
    assert any(n["title"] == "Tagged" for n in r.json())


def test_search_by_keyword():
    client.post("/api/notes", json={"title": "Unique needle"}, headers=HEADERS)
    r = client.get("/api/notes/search?q=needle", headers=HEADERS)
    assert r.status_code == 200
    assert any("needle" in n["title"] for n in r.json())


def test_auth_rejected():
    r = client.get("/api/notes", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_auth_missing():
    r = client.get("/api/notes")
    assert r.status_code == 401


def test_validation_empty_title():
    r = client.post("/api/notes", json={"title": ""}, headers=HEADERS)
    assert r.status_code == 422
