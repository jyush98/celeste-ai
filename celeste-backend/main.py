from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime
import os


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Celeste backend is live"}

@app.post("/generate-jewelry-image")
def generate_image():
    source_path="test_image.png"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    target_path = f"static/generated/output_{timestamp}.png"

    with open(source_path, "rb") as src, open(target_path, "wb") as dst:
        dst.write(src.read())

    return {
        "image_url": f"static/generated/output_{timestamp}.png"
    }