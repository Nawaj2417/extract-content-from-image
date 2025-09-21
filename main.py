import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API client with your API key
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=API_KEY)

# Initialize the FastAPI application
app = FastAPI(
    title="Gemini Image Text Extractor",
    description="A simple API to extract text from an uploaded image using the Gemini Vision model.",
    version="1.0.0",
)

# Initialize the Gemini Vision model
try:
    vision_model = genai.GenerativeModel('gemini-pro-vision')
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to initialize Gemini model: {e}")

@app.post("/extract-text")
async def extract_text_from_image(file: UploadFile = File(...)):
    """
    Extracts text from an uploaded image file.

    - **file**: The image file to be processed (e.g., JPEG, PNG).
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are supported.")

    try:
        # Read the image file into a bytes buffer
        image_bytes = await file.read()
        image_stream = io.BytesIO(image_bytes)

        # Open the image using PIL (Pillow)
        image = Image.open(image_stream)

        # Define the prompt for the model
        prompt = "Extract all text from this image."

        # Send the image and prompt to the Gemini model
        response = vision_model.generate_content([prompt, image])

        # Extract the text from the model's response
        extracted_text = response.text

        # Return the extracted text in a JSON response
        return JSONResponse(content={"extracted_text": extracted_text})

    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the image and extract text. Please try again.")

@app.get("/")
def read_root():
    """
    Returns a simple welcome message.
    """
    return {"message": "Welcome to the Gemini Image Text Extractor API!"}
