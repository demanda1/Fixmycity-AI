import cv2
import numpy as np
import pytesseract

def extract_text_from_image(image_path: str) -> dict:
    img = cv2.imread(image_path)

    if img is None:
        return {"error":"Could not read image"}

    # Convert to greyscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresolding to handle poor lighting
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)


    # Denoise
    gray = cv2.medianBlur(gray, 3)

    # Run OCR
    raw_text = pytesseract.image_to_string(gray, lang="eng")
    cleaned_text = raw_text.strip()

    # Try to detect useful info
    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

    response = {
        "raw_text": cleaned_text,
        "lines_found": lines,
        "num_lines": len(lines),
        "has_text": len(cleaned_text) > 0
    }

    return response
