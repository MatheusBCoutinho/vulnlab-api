from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def auth(user, password):
    token = client.post("/login", params={"username": user, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_idor_visible_in_lab():
    headers = auth("alice", "alice123")
    response = client.get("/lab/invoices/2", headers=headers)
    assert response.status_code == 200
    assert response.json()["owner_id"] == 2

def test_idor_blocked_in_secure():
    headers = auth("alice", "alice123")
    assert client.get("/secure/invoices/2", headers=headers).status_code == 403
    assert client.get("/secure/invoices/1", headers=headers).status_code == 200

def test_requires_auth():
    assert client.get("/lab/invoices/1").status_code in (401, 403)
