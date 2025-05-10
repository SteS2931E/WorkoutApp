from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from dotenv import load_dotenv
import base64
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize FastAPI app (only ONCE)
app = FastAPI()

# Enable CORS so your frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility function to base64-encode image
def encode_image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

# Endpoint 1: Generic image description
@app.post("/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        image_base64 = encode_image_to_base64(image_bytes)

        if "image" not in image.content_type:
            raise HTTPException(status_code=400, detail="Invalid image file type")

        model = genai.GenerativeModel("gemini-pro-vision")
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

# Endpoint 2: Nutritionist recipe generation
@app.post("/generate-recipe")
async def generate_recipe(image: UploadFile = File(...)):
    try:
        if "image" not in image.content_type:
            raise HTTPException(status_code=400, detail="File is not an image.")

        image_bytes = await image.read()
        image_base64 = encode_image_to_base64(image_bytes)

        prompt = (
            "You are a certified nutritionist. Analyze the ingredients in this image "
            "and create a healthy recipe using them. "
            "Include:\n"
            "- Name of the dish\n"
            "- List of ingredients with measurements\n"
            "- Step-by-step cooking instructions\n"
            "- Estimated calories per serving\n"
            "- Macronutrient breakdown\n"
            "- Health benefits\n"
            "- Portion size suggestion"
        )

        model = genai.GenerativeModel("gemini-pro-vision")
        response = model.generate_content([
            prompt,
            {
                "inlineData": {
                    "mimeType": image.content_type,
                    "data": image_base64,
                }
            }
        ])
        return {"recipe": response.text}
    except Exception as e:
        return {"error": str(e)}
