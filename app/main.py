from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from app.core.script_generator import ScriptGenerator
from app.core.scene_grouper import SceneGrouper
from app.core.panel_detector import PanelDetector
import tempfile
import os

app = FastAPI()

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

@app.post("/recap")
async def generate_recap(request: RecapRequest):
    generator = ScriptGenerator(
        title=request.title,
        characters=request.characters
    )
    recap = generator.generate_dramatic_recap()
    return {"recap": recap}

@app.post("/scenes")
async def group_scenes(request: ScenesRequest):
    panels = [(p.x, p.y, p.w, p.h) for p in request.panels]
    grouper = SceneGrouper(row_threshold=request.row_threshold)
    scenes = grouper.group_scenes(panels)
    return {"scenes": scenes, "total_scenes": len(scenes)}

@app.post("/panels")
async def detect_panels(file: UploadFile = File(...), min_area: int = 500):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        detector = PanelDetector(min_area=min_area)
        panels = detector.detect_panels(tmp_path)
        return {
            "filename": file.filename,
            "panels_found": len(panels),
            "panels": [{"x": p[0], "y": p[1], "w": p[2], "h": p[3]} for p in panels]
        }
    finally:
        os.unlink(tmp_path)
