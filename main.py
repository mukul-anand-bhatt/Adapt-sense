import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from conversion_braille import convert_to_braille, convert_to_english  # Import conversion functions
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sign import text_to_sign_stream
from fastapi import FastAPI, HTTPException, File, UploadFile
import google.generativeai as genai
from PIL import Image
import io
from dotenv import load_dotenv


app = FastAPI()

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")


# Added CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (Update for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Request Model
class TextRequest(BaseModel):
    text: str

# Endpoint to convert English to Braille
@app.post("/to_braille")
def to_braille(request: TextRequest):
    return {"braille": convert_to_braille(request.text)}

# Endpoint to convert Braille to English
@app.post("/to_english")
def to_english(request: TextRequest):
    return {"english": convert_to_english(request.text)}

# Sign Language Video Streaming Endpoint
@app.get("/stream_sign_images")
async def stream_sign_images(text: str):
    """API endpoint to stream sign language images based on input text."""
    return StreamingResponse(text_to_sign_stream(text), media_type="multipart/x-mixed-replace; boundary=frame")

# ✅ New Endpoint: Image to Text using Google Gemini API
@app.post("/image_to_text/")
async def image_to_text(file: UploadFile = File(...)):
    """Extracts text from an image using Google Gemini API."""
    try:
        # Read image from uploaded file
        image = Image.open(io.BytesIO(await file.read()))

        # Generate description with an assistive prompt
        response = model.generate_content(["Tell me about this picture in such a way that you are assisting a blind person", image])

        return {"extracted_text": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI application on the correct port
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Get port from environment variable, default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
