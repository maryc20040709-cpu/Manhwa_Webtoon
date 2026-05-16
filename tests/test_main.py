from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Manhwa Webtoon API!"}

def test_recap_basic():
    response = client.post("/recap", json={
        "title": "Solo Leveling",
        "characters": ["Sung Jinwoo", "Cha Hae-In"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "recap" in data
    assert isinstance(data["recap"], str)
    assert len(data["recap"]) > 0

def test_recap_empty_characters():
    response = client.post("/recap", json={
        "title": "Tower of God",
        "characters": []
    })
    assert response.status_code == 200
    data = response.json()
    assert "recap" in data
    assert "Tower of God" in data["recap"]

def test_recap_missing_title():
    response = client.post("/recap", json={
        "characters": ["Bam"]
    })
    assert response.status_code == 422

def test_recap_missing_characters():
    response = client.post("/recap", json={
        "title": "Tower of God"
    })
    assert response.status_code == 422
