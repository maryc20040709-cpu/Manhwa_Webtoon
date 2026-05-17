from fastapi import FastAPI
from pydantic import BaseModel
from app.core.script_generator import ScriptGenerator
from app.core.scene_grouper import SceneGrouper

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
