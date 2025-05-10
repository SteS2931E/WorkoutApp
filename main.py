from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
import base64
import os

load_dotenv()
configure(api_key=os.getenv("AIzaSyAIu8QNSVxgTNZJ5bS_FfN_7Wn3A5Cg3gM"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        model = GenerativeModel("gemini-pro-vision")
        response = model.generate_content([
            "What is in this image?",
            {
                "inlineData": {
                    "mimeType": image.content_type,
                    "data": image_base64,
                }
            }
        ])
        return {"result": response.text}
    except Exception as e:
        return {"error": str(e)}
