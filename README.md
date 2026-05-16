# 📖 Manhwa Webtoon API

A FastAPI-based REST API for analyzing Manhwa and Webtoon content using computer vision — detecting panels, grouping scenes, and generating dramatic episode recaps.

## ✨ Features

- **Panel Detector** — identifies and extracts individual panels from Manhwa/Webtoon pages
- **Scene Grouper** — groups related panels into coherent scenes
- **Vision Analyzer** — analyzes visual content of panels
- **Script Generator** — auto-generates dramatic episode recap text

## 🗂️ Project StructureManhwa_Webtoon/
├── app/
│   ├── main.py
│   ├── config.py
│   └── core/
│       ├── panel_detector.py
│       ├── scene_grouper.py
│       ├── script_generator.py
│       └── vision_analyzer.py
└── README.md

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
uvicorn app.main:app --reload
```

API: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Health check |

## 🗺️ Roadmap

- [ ] Fix f-string bug in script_generator.py
- [ ] Connect core modules to API endpoints
- [ ] Add requirements.txt and .env.example
- [ ] Add tests (pytest)
- [ ] LLM integration for smarter recaps

## 📄 License

MIT
