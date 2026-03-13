import cv2
import pytesseract

from services.mrz_service import detect_mrz, parse_mrz, fix_ocr_line
from utils.image_utils import deskew


def scan_passport_image(img):

    img = deskew(img)

    h, w = img.shape[:2]

    # crop MRZ
    mrz = detect_mrz(img)

    if mrz is None:
        mrz = img[int(h * 0.65):h, 0:w]

    # resize giúp OCR chính xác hơn
    mrz = cv2.resize(
        mrz,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(mrz, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # save debug
    cv2.imwrite("debug/img_goc.jpg", img)
    cv2.imwrite("debug/mrz_crop.jpg", mrz)
    cv2.imwrite("debug/mrz_thresh.jpg", thresh)

    config = "--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"

    text = pytesseract.image_to_string(thresh, config=config)

    print("===== RAW OCR =====")
    print(text)

    lines = text.split("\n")

    mrz_lines = []

    for l in lines:

        l = fix_ocr_line(l)

        if "P<" in l:
            l = l[l.index("P<"):]

        if l.startswith("P<"):
            l = l.ljust(44, "<")
            mrz_lines.insert(0, l)

        elif len(l) > 30 and "<" in l:
            mrz_lines.append(l)

    print("MRZ lines:", mrz_lines)

    data = parse_mrz(mrz_lines)

    success = data is not None

    return {
        "success": success,
        "data": data,
        "mrz_lines": mrz_lines,
        "raw_text": text,
        "message": "Scan thành công" if success else "Không đọc được MRZ"
    }