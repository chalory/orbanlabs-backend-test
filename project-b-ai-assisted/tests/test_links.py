import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app
from database import DB_PATH, init_db, get_connection

client = TestClient(app, follow_redirects=False)
HEADERS = {"X-API-Key": "dev-api-key"}


@pytest.fixture(autouse=True)
def clean_db():
    init_db()
    yield
    conn = get_connection()
    conn.execute("DELETE FROM urls")
    conn.commit()
    conn.close()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_create_link():
    r = client.post("/api/links", json={"original_url": "https://example.com"}, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["original_url"] == "https://example.com"
    assert len(data["short_code"]) == 6
    assert data["click_count"] == 0


def test_create_with_custom_code():
    r = client.post(
        "/api/links",
        json={"original_url": "https://example.com/custom", "custom_code": "mycode"},
        headers=HEADERS,
    )
    assert r.status_code == 201
    assert r.json()["short_code"] == "mycode"


def test_duplicate_url_returns_existing():
    r1 = client.post("/api/links", json={"original_url": "https://example.com/dup"}, headers=HEADERS)
    r2 = client.post("/api/links", json={"original_url": "https://example.com/dup"}, headers=HEADERS)
    assert r1.json()["short_code"] == r2.json()["short_code"]


def test_duplicate_code_rejected():
    client.post(
        "/api/links",
        json={"original_url": "https://a.com", "custom_code": "taken"},
        headers=HEADERS,
    )
    r = client.post(
        "/api/links",
        json={"original_url": "https://b.com", "custom_code": "taken"},
        headers=HEADERS,
    )
    assert r.status_code == 409


def test_list_links():
    client.post("/api/links", json={"original_url": "https://one.com"}, headers=HEADERS)
    client.post("/api/links", json={"original_url": "https://two.com"}, headers=HEADERS)
    r = client.get("/api/links", headers=HEADERS)
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_redirect():
    r = client.post(
        "/api/links",
        json={"original_url": "https://example.com/redir", "custom_code": "gohere"},
        headers=HEADERS,
    )
    r = client.get("/gohere")
    assert r.status_code == 307
    assert r.headers["location"] == "https://example.com/redir"


def test_redirect_increments_clicks():
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/clicks", "custom_code": "countme"},
        headers=HEADERS,
    )
    client.get("/countme")
    client.get("/countme")
    r = client.get("/api/links/countme/stats", headers=HEADERS)
    assert r.json()["click_count"] == 2


def test_stats():
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/stats", "custom_code": "mystats"},
        headers=HEADERS,
    )
    r = client.get("/api/links/mystats/stats", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["short_code"] == "mystats"
    assert r.json()["click_count"] == 0


def test_stats_not_found():
    r = client.get("/api/links/nope/stats", headers=HEADERS)
    assert r.status_code == 404


def test_delete_link():
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/del", "custom_code": "byebye"},
        headers=HEADERS,
    )
    r = client.delete("/api/links/byebye", headers=HEADERS)
    assert r.status_code == 204
    r = client.get("/api/links/byebye/stats", headers=HEADERS)
    assert r.status_code == 404


def test_redirect_missing_code():
    r = client.get("/doesnotexist")
    assert r.status_code == 404


def test_invalid_url():
    r = client.post("/api/links", json={"original_url": "not-a-url"}, headers=HEADERS)
    assert r.status_code == 422


def test_auth_rejected():
    r = client.post("/api/links", json={"original_url": "https://example.com"}, headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_auth_missing():
    r = client.get("/api/links")
    assert r.status_code == 401


def test_redirect_is_public():
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/pub", "custom_code": "public"},
        headers=HEADERS,
    )
    r = client.get("/public")
    assert r.status_code == 307
