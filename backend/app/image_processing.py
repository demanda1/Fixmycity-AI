import cv2
import numpy as np
import os
from datetime import datetime


UPLOAD_DIR = os.path.join("data", "uploads")


def save_and_preprocess_image(file_bytes: bytes, complaint_id: int) -> dict:
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"complaint_{complaint_id}_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save original
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    # Read with OpenCV
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image file"}

    # Get image info
    height, width, channels = img.shape

    # Preprocess: resize if too large (keep under 1024px width)
    max_width = 1024
    if width > max_width:
        scale = max_width / width
        img = cv2.resize(img, None, fx=scale, fy=scale)
        height, width = img.shape[:2]

    # Calculate basic image quality metrics
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)

    # Save preprocessed version
    processed_filename = f"processed_{filename}"
    processed_path = os.path.join(UPLOAD_DIR, processed_filename)
    cv2.imwrite(processed_path, img)

    response = {
        "original_path": filepath,
        "processed_path": processed_path,
        "width": width,
        "height": height,
        "blur_score": round(blur_score, 2),
        "brightness": round(brightness, 2),
        "is_blurry": bool(blur_score < 100),
        "is_too_dark": bool(brightness < 50)
    }
    return response