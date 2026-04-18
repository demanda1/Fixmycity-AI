from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.app.models import ComplaintCreate, ComplaintResponse, IssueStatus
from backend.app.database import get_connection
from typing import List
from backend.app.image_processing import save_and_preprocess_image
from backend.app.ai_classifier import classify_image
from backend.app.ocr_service import extract_text_from_image


router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/", response_model=ComplaintResponse, status_code=201)
async def create_complaint(complaint: ComplaintCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (description, latitude, longitude, ward, city, reporter_name, reporter_email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint.description,
        complaint.latitude,
        complaint.longitude,
        complaint.ward,
        complaint.city,
        complaint.reporter_name,
        complaint.reporter_email
    ))
    conn.commit()
    complaint_id = cursor.lastrowid

    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row)


@router.get("/", response_model=List[ComplaintResponse])
async def get_all_complaints(city: str = None, status: IssueStatus = None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if city:
        query += " AND city = ?"
        params.append(city)
    if status:
        query += " AND status = ?"
        params.append(status.value)

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return dict(row)

@router.post("/{complaint_id}/upload-image")
async def upload_complaint_image(complaint_id: int, file: UploadFile = File(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Complaint not found")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_bytes = await file.read()
    result = save_and_preprocess_image(file_bytes, complaint_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # AI Classification
    ai_result = await classify_image(result["processed_path"], dict(row)["description"])

    # Update complaint with image path + AI classification
    cursor.execute("""
        UPDATE complaints 
        SET image_path = ?, category = ?, severity = ?
        WHERE id = ?
    """, (
        result["processed_path"],
        ai_result["category"],
        ai_result["severity"],
        complaint_id
    ))
    conn.commit()
    conn.close()

    response = {
        "message": "Image uploaded, processed, and classified",
        "complaint_id": complaint_id,
        "image_info": result,
        "ai_classification": ai_result
    }

    return response

@router.get("/{complaint_id}/extract-text")
async def extract_text_from_complaint_image(complaint_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Complaint not found")

    row_dict = dict(row)
    if not row_dict.get("image_path"):
        raise HTTPException(status_code=400, detail="No image uploaded for this complaint")

    result = extract_text_from_image(row_dict["image_path"])

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    response = {
        "complaint_id": complaint_id,
        "ocr_result": result
    }

    return response