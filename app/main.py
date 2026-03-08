from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}

# Additional routes can be initialized here...