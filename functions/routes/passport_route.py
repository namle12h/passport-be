from fastapi import APIRouter, UploadFile, File
import numpy as np
import cv2
from datetime import datetime

from services.ocr_service import scan_passport_image
from services.drive_service import upload_to_drive

router = APIRouter()

@router.post("/api/scan-passport")
async def scan_passport(file: UploadFile = File(...)):

    contents = await file.read()

    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result = scan_passport_image(img)

    filename = f"passport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = f"debug/{filename}"

    cv2.imwrite(filepath, img)

    drive_id = upload_to_drive(filepath, filename)

    result["drive_url"] = f"https://drive.google.com/file/d/{drive_id}/view"

    return result


@router.get("/")
def home():
    return {"status": "passport OCR API running"}