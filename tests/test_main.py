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

def test_scenes_basic():
    response = client.post("/scenes", json={
        "panels": [
            {"x": 10, "y": 20, "w": 200, "h": 150},
            {"x": 220, "y": 25, "w": 200, "h": 150},
            {"x": 10, "y": 300, "w": 200, "h": 150}
        ],
        "row_threshold": 50
    })
    assert response.status_code == 200
    data = response.json()
    assert "scenes" in data
    assert "total_scenes" in data
    assert data["total_scenes"] == 2

def test_scenes_empty_panels():
    response = client.post("/scenes", json={
        "panels": [],
        "row_threshold": 50
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_scenes"] == 0

def test_panels_upload():
    import numpy as np
    import cv2
    import io
    img = np.ones((400, 600, 3), dtype=np.uint8) * 240
    cv2.rectangle(img, (20, 20), (280, 180), (0, 0, 0), 3)
    cv2.rectangle(img, (320, 20), (580, 180), (0, 0, 0), 3)
    cv2.rectangle(img, (20, 220), (580, 380), (0, 0, 0), 3)
    _, buffer = cv2.imencode('.jpg', img)
    image_bytes = io.BytesIO(buffer.tobytes())
    response = client.post(
        "/panels",
        files={"file": ("test.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "panels_found" in data
    assert data["panels_found"] > 0
