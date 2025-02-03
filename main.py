import os
import uvicorn
from pydantic import BaseModel
from conversion_braille import convert_to_braille, convert_to_english
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sign import text_to_sign_stream
from fastapi import FastAPI, HTTPException, File, UploadFile
import google.generativeai as genai
import requests
import base64
from dotenv import load_dotenv
from PIL import Image
import io


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
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class TextRequest(BaseModel):
    text: str

# ✅ Endpoint: Convert English to Braille
@app.post("/to_braille")
def to_braille(request: TextRequest):
    return {"braille": convert_to_braille(request.text)}

# ✅ Endpoint: Convert Braille to English
@app.post("/to_english")
def to_english(request: TextRequest):
    return {"english": convert_to_english(request.text)}

# ✅ Endpoint: Sign Language Video Streaming
@app.get("/stream_sign_images")
async def stream_sign_images(text: str):
    return StreamingResponse(text_to_sign_stream(text), media_type="multipart/x-mixed-replace; boundary=frame")

# ✅ Endpoint: Image to Text using Google Gemini API
@app.post("/image_to_text/")
async def image_to_text(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read()))
        response = model.generate_content(["Tell me about this picture in such a way that you are assisting a blind person", image])
        return {"extracted_text": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Endpoint: Text-to-Speech using Google Text-to-Speech API
@app.post("/text_to_speech/")
async def text_to_speech(request: TextRequest):
    try:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"

        # Prepare API request data
        data = {
            "input": {"text": request.text},
            "voice": {"languageCode": "en-US", "ssmlGender": "NEUTRAL"},
            "audioConfig": {"audioEncoding": "MP3"}
        }

        # Send request to Google Text-to-Speech API
        response = requests.post(url, json=data)
        response_json = response.json()

        # Check if the response contains audio content
        if "audioContent" not in response_json:
            raise HTTPException(status_code=500, detail="Error generating speech")

        # Decode the base64-encoded audio content
        audio_data = base64.b64decode(response_json["audioContent"])

        # Write the raw audio data to a file
        audio_file_path = "output.mp3"
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(audio_data)

        return {"message": "Audio file saved", "audio_file": audio_file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Speech to Text End Point
@app.post("/speech_to_text/")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_API_KEY}"
        
        # Read and encode the audio file to base64
        audio_data = base64.b64encode(await file.read()).decode("utf-8")

        # Prepare API request payload
        data = {
            "config": {
                "encoding": "MP3",  # Ensure encoding matches the audio format
                "languageCode": "en-US"
            },
            "audio": {
                "content": audio_data  # Send base64-encoded content
            }
        }

        # Send request to Google Speech-to-Text API
        response = requests.post(url, json=data)
        result = response.json()

        # Extract transcribed text if available
        if "results" in result:
            transcript = " ".join([res["alternatives"][0]["transcript"] for res in result["results"]])
            return {"transcribed_text": transcript}
        else:
            return {"error": "No transcription available", "response": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Run FastAPI Application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
