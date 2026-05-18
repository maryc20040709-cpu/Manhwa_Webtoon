# 📖 Manhwa Webtoon API
![CI](https://github.com/maryc20040709-cpu/Manhwa_Webtoon/actions/workflows/ci.yml/badge.svg)

A FastAPI-based REST API for analyzing Manhwa and Webtoon content using computer vision — detecting panels, grouping scenes, and generating dramatic episode recaps.

## ✨ Features

- **Panel Detector** — detects panels in Manhwa images using OpenCV (computer vision)
- **Scene Grouper** — groups panels into scenes by vertical position
- **Script Generator** — generates dramatic episode recap text
- **FastAPI** — fast, modern Python web framework with automatic Swagger docs
- **File Upload** — upload images directly to the API
- - **Web Frontend** — simple HTML interface at `/static/index.html`

## 🗂️ Project Structure
Manhwa_Webtoon/
├── app/
│   ├── main.py
│   ├── config.py
│   └── core/
│       ├── panel_detector.py
│       ├── scene_grouper.py
│       ├── script_generator.py
│       └── vision_analyzer.py
├── tests/
│   ├── test_main.py
│   └── test_script_generator.py
├── .env.example
├── .gitignore
└── requirements.txt

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/maryc20040709-cpu/Manhwa_Webtoon.git
cd Manhwa_Webtoon
pip install -r requirements.txt
```

### Run the App

```bash
python3 -m uvicorn app.main:app --reload
```

API: `http://localhost:8000` | Swagger UI: `http://localhost:8000/docs`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/recap` | Generate dramatic episode recap |
| POST | `/scenes` | Group panels into scenes |
| POST | `/panels` | Detect panels in uploaded image |
| POST | `/analyze` | Full analysis: panels + scenes + recap |
## 🔍 Example Response

`POST /analyze` with `test_manhwa.jpg`, title `Solo Leveling`, characters `Sung Jinwoo,Cha Hae-In`:

```json
{
  "filename": "test_manhwa.jpg",
  "panels_found": 5,
  "total_scenes": 3,
  "recap": "Emotions run high in 'Solo Leveling', as Cha Hae-In struggles with personal conflicts that impact their relationships."
}
```

## 🧪 Tests

```bash
python3 -m pytest tests/ -v
```

16 tests — all passing ✅

## 📄 License

MIT
