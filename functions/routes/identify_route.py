# from fastapi import APIRouter, UploadFile, File,BackgroundTasks
# import numpy as np
# import cv2

# from services.qr_service import detect_qr
# from services.cccd_parser import parse_cccd_qr
# from validators.cccd_validator import validate_cccd_qr
# from services.drive_service import upload_to_drive
# from datetime import datetime
# import tempfile
# router = APIRouter()


# @router.post("/api/scan-cccd")
# async def scan_cccd(background_tasks: BackgroundTasks,file: UploadFile = File(...)):

#     contents = await file.read()

#     nparr = np.frombuffer(contents, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     # cv2.imwrite("debug_original.jpg", img)

#     qr_data = detect_qr(img)

#     if not qr_data:
#         return {
#             "success": False,
#             "message": "QR not detected"
#         }

#     print("QR RAW:", qr_data)

#     # validate QR trước
#     validated = validate_cccd_qr(qr_data)

#     if not validated:
#         return {
#             "success": False,
#             "message": "Invalid CCCD data"
#         }

#     # parse sau
#     parsed = parse_cccd_qr(qr_data)
    
#     filename = f"cccd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

#     # tạo file tạm
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
#         tmp.write(contents)
#         tmp_path = tmp.name

#     filename = f"cccd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#     background_tasks.add_task(upload_to_drive, tmp_path, filename)

#     return {
#         "success": True,
#         "data": parsed,
#         "drive_url": "uploading"

#     }

from fastapi import APIRouter, UploadFile, File, BackgroundTasks
import numpy as np
import cv2
from datetime import datetime
import tempfile

from services.qr_service import detect_qr
from services.cccd_parser import parse_cccd_qr
from validators.cccd_validator import validate_cccd_qr
from services.drive_service import upload_to_drive

router = APIRouter()


@router.post("/api/scan-cccd")
async def scan_cccd(
    background_tasks: BackgroundTasks,
    front: UploadFile = File(...),
    back: UploadFile = File(...)
):

    # đọc ảnh front
    front_bytes = await front.read()
    front_np = np.frombuffer(front_bytes, np.uint8)
    front_img = cv2.imdecode(front_np, cv2.IMREAD_COLOR)

    # đọc ảnh back
    back_bytes = await back.read()
    back_np = np.frombuffer(back_bytes, np.uint8)
    back_img = cv2.imdecode(back_np, cv2.IMREAD_COLOR)

    if front_img is None or back_img is None:
        return {
            "success": False,
            "message": "Invalid image"
        }

    # thử scan QR ảnh front
    qr_data = detect_qr(front_img)

    # nếu front không có QR thì scan back
    if not qr_data:
        qr_data = detect_qr(back_img)

    if not qr_data:
        return {
            "success": False,
            "message": "QR not detected"
        }

    print("QR RAW:", qr_data)

    # validate CCCD
    validated = validate_cccd_qr(qr_data)

    if not validated:
        return {
            "success": False,
            "message": "Invalid CCCD data"
        }

    parsed = parse_cccd_qr(qr_data)

    # lưu ảnh tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(front_bytes)
        tmp_path = tmp.name

    filename = f"cccd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    background_tasks.add_task(upload_to_drive, tmp_path, filename)

    return {
        "success": True,
        "data": parsed,
        "drive_url": "uploading"
    }