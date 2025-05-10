from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv
import base64
import os

# Load environment variables
load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (so frontend can talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the /upload endpoint
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

