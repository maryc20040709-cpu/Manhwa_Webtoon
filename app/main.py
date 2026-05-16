from fastapi import FastAPI
from pydantic import BaseModel
from app.core.script_generator import ScriptGenerator

app = FastAPI()


class RecapRequest(BaseModel):
    title: str
    characters: list[str]


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