from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
import cv2
import time

app = FastAPI()

SIGN_DATA_FOLDER = "Sign-Data"  # Update this path if needed

def text_to_sign_stream(text: str):
    """Generator function to stream sign images based on input text."""
    text = text.lower()  # Normalize text to lowercase

    for char in text:
        img_path = os.path.join(SIGN_DATA_FOLDER, f"{char}.jpg")  # Assuming images are named 'a.jpg', 'b.jpg', etc.
        
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            _, img_encoded = cv2.imencode(".jpg", img)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + img_encoded.tobytes() + b"\r\n")
            time.sleep(0.5)  # Delay for streaming effect (adjust as needed)
        else:
            print(f"Warning: Image for '{char}' not found.")

