from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.core.script_generator import ScriptGenerator
from app.core.scene_grouper import SceneGrouper
from app.core.panel_detector import PanelDetector
import tempfile
import os

app = FastAPI(title="Manhwa/Webtoon Analyzer")

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
    return {"message": "Welcome to the Manhwa Webtoon API!"}

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
    file: UploadFile = File(...),
    title: str = "Unknown",
    characters: str = "",
    lang: str = "en",
    genre: str = "",
    min_area: int = 500,
    row_threshold: int = 50
):
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
        generator = ScriptGenerator(title=title, characters=chars, lang=lang)
        recap = generator.generate_dramatic_recap()
        result_id = save_analysis(
            title, characters, len(panels), len(scenes), recap,
            genre=genre or None
        )
        return {
            "filename": file.filename,
            "panels_found": len(panels),
            "total_scenes": len(scenes),
            "recap": recap,
            "result_id": result_id,
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
