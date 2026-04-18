from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GENAI_APIKEY")
client = genai.Client(api_key=api_key)

async def classify_image(image_path: str, description: str) -> dict:

    # Load image
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        
    # Standard Gemini upload
    uploaded_file = client.files.upload(file=image_path)

    prompt = f"""You are a civic issue classifier for Indian cities. A citizen reported this issue: " {description}"
    they also reported the attached photo. 

    Analyse the photo and respond with ONLY a JSON object (no markdown, no backticks):
    {{
        "category": one of ["pothole","garbage","drain","streetlight","road_damage","other"],
        "severity": one of ["low", "medium", "high", "critical"]
        "confidence": a number between 0 and 1,
        "ai_description": "brief 1-2 line description of what you see in the image",
        "department": one of ["Roads", "Sanitation", "Drainage", "Electrical", "Genral"]
    }}
    """

    response = client.models.generate_content( model="gemini-2.5-flash", contents=[prompt, uploaded_file])
    response_text = response.text.strip()

    # Clean markdown backticks if present
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.split("```", 1)[0].strip()

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "category": "other",
            "severity": "medium",
            "confidence": 0.0,
            "ai_description": "Could not analyze image",
            "department": "General"
        }

    return result