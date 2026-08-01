from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.core.script_generator import ScriptGenerator, GeminiAnalyzer
from app.core.scene_grouper import SceneGrouper
from app.core.panel_detector import PanelDetector
from collections import defaultdict
import tempfile
import os
import time

app = FastAPI(title="Manhwa/Webtoon Analyzer")

# ── Simple in-memory rate limit for /analyze ────────────────────────────────
# Keeps the free Groq quota from being burned by one visitor (accidental
# reload-spam or abuse). In-memory is fine here: Render's free tier runs a
# single instance, and it's OK if the counters reset on restart/deploy.
RATE_LIMIT_WINDOW = 300   # seconds
RATE_LIMIT_MAX = 15       # requests per IP per window
_rate_limit_hits: dict[str, list[float]] = defaultdict(list)

def _enforce_rate_limit(ip: str):
    now = time.time()
    hits = _rate_limit_hits[ip]
    cutoff = now - RATE_LIMIT_WINDOW
    while hits and hits[0] < cutoff:
        hits.pop(0)
    if len(hits) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a few minutes and try again.",
        )
    hits.append(now)

from fastapi.staticfiles import StaticFiles
from app.database import init_db, save_analysis, get_history, get_total_count, get_analysis_by_id

init_db()

class RecapRequest(BaseModel):
    title: str
    characters: list[str]

class Panel(BaseModel):
    x: int
    y: int
    w: int
    h: int

class ScenesRequest(BaseModel):
    panels: list[Panel]
    row_threshold: int = 50

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    """Lightweight endpoint the frontend pings to detect/trigger a cold start."""
    return {"status": "ok"}

@app.get("/robots.txt")
async def robots():
    return FileResponse("static/robots.txt")

@app.get("/stats")
def get_stats():
    return {"total_analyses": get_total_count()}

@app.post("/recap")
async def generate_recap(request: RecapRequest):
    generator = ScriptGenerator(title=request.title, characters=request.characters)
    return {"recap": generator.generate_dramatic_recap()}

@app.post("/scenes")
async def group_scenes(request: ScenesRequest):
    panels = [(p.x, p.y, p.w, p.h) for p in request.panels]
    grouper = SceneGrouper(row_threshold=request.row_threshold)
    scenes = grouper.group_scenes(panels)
    return {"scenes": scenes, "total_scenes": len(scenes)}

@app.post("/panels")
async def detect_panels(file: UploadFile = File(...), min_area: int = 500):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG files allowed")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(data); tmp_path = tmp.name
    try:
        detector = PanelDetector(min_area=min_area)
        panels = detector.detect_panels(tmp_path)
        return {"filename": file.filename, "panels_found": len(panels),
                "panels": [{"x": p[0], "y": p[1], "w": p[2], "h": p[3]} for p in panels]}
    finally:
        os.unlink(tmp_path)

@app.post("/analyze")
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    title: str = "",
    characters: str = "",
    lang: str = "en",
    genre: str = "",
    min_area: int = 500,
    row_threshold: int = 50
):
    client_ip = request.client.host if request.client else "unknown"
    _enforce_rate_limit(client_ip)

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG files allowed")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(data); tmp_path = tmp.name
    try:
        detector = PanelDetector(min_area=min_area)
        panels = detector.detect_panels(tmp_path)
        grouper = SceneGrouper(row_threshold=row_threshold)
        scenes = grouper.group_scenes(panels)
        chars = [c.strip() for c in characters.split(",") if c.strip()]

        # ── Try real AI analysis first ──────────────────────────────────────
        ai_mood = None
        gemini  = GeminiAnalyzer()
        ai      = gemini.analyze(
            data, file.content_type or "image/jpeg",
            title, chars, lang
        )
        if ai:
            recap   = ai["recap"]
            ai_mood = ai["mood"]       # e.g. "drama" — sent to frontend
        else:
            # Fall back to template-based recap
            generator = ScriptGenerator(title=title, characters=chars, lang=lang)
            recap     = generator.generate_dramatic_recap()

        result_id = save_analysis(
            title, characters, len(panels), len(scenes), recap,
            genre=genre or None
        )
        return {
            "filename":     file.filename,
            "panels_found": len(panels),
            "total_scenes": len(scenes),
            "recap":        recap,
            "mood":         ai_mood,   # None when template was used
            "result_id":    result_id,
            "ai_powered":   ai is not None,
        }
    finally:
        os.unlink(tmp_path)

@app.get("/result/{result_id}")
def get_result(result_id: str):
    result = get_analysis_by_id(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

@app.get("/history")
def get_analysis_history(limit: int = 10):
    return get_history(limit)

app.mount("/static", StaticFiles(directory="static"), name="static")
