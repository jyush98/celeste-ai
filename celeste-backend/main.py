from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import requests
import replicate
import os

load_dotenv()
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

HF_TOKEN = os.getenv("HF_TOKEN")
client = InferenceClient(api_key=HF_TOKEN)
class PromptInput(BaseModel):
    prompt: str


@app.post("/generate-jewelry-image-inference")
def generate_image(input: PromptInput, request: Request):
    prompt = input.prompt
    
    print("Received prompt:", prompt)

    try:
        image = client.text_to_image(prompt, model="runwayml/stable-diffusion-v1-5")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"output_{timestamp}.png"
        filepath = f"static/generated/{filename}"

        image.save(filepath)  # Save the PIL image

        return {"image_url": f"/static/generated/{filename}"}

    except Exception as e:
        print("Inference error:", repr(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-jewelry-image-not-working")
def generate_image(data: PromptInput, request: Request):
    prompt = data.prompt
    print("Prompt received:", prompt)

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api-inference.huggingface.co/stabilityai/stable-diffusion-2",
        headers=headers,
        json={"inputs": prompt}
    )

    print("Response status:", response.status_code)
    if response.status_code != 200 or "image" not in response.headers.get("Content-Type", ""):
        print("HF Error:", response.text)
        return JSONResponse(status_code=500, content={"error": "Image generation failed"})

    # Save image
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"output_{timestamp}.png"
    filepath = f"static/generated/{filename}"

    with open(filepath, "wb") as f:
        f.write(response.content)

    return {"image_url": f"/static/generated/{filename}"}

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
replicate.Client(api_token=REPLICATE_API_TOKEN)

@app.post("/generate-jewelry-image")
def generate_image(data: PromptInput, request: Request):
    prompt = data.prompt
    print("Prompt received:", prompt)

    try:
        # Run the model on Replicate
        output_url = replicate.run(
            "lucataco/sdxl:fc548c732c30d8a4df984e3c9c1d3f066e400cd02026b96eeb2663a045a3ed4e",
            input={
                "prompt": prompt,
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024
            }
        )

        if isinstance(output_url, list):
            output_url = output_url[0]  # grab first image URL

        if not output_url or not output_url.startswith("http"):
            raise ValueError("Invalid image URL from Replicate")

        # Download the image from the URL
        image_data = requests.get(output_url).content

        # Save to local static directory
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"output_{timestamp}.png"
        filepath = f"static/generated/{filename}"

        with open(filepath, "wb") as f:
            f.write(image_data)

        return {"image_url": f"/static/generated/{filename}"}

    except Exception as e:
        print("Replicate error:", repr(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
