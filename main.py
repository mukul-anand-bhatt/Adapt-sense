import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from conversion_braille import convert_to_braille, convert_to_english  # Import conversion functions
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sign import text_to_sign_stream

app = FastAPI()

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

# Run the FastAPI application on the correct port
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Get port from environment variable, default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
