import cv2
import numpy as np
import re
from datetime import datetime


# =========================
# format date
# =========================
def format_date(date_str, is_expiry=False):

    if len(date_str) != 6 or not date_str.isdigit():
        return None

    yy = int(date_str[0:2])
    mm = int(date_str[2:4])
    dd = int(date_str[4:6])

    if mm < 1 or mm > 12 or dd < 1 or dd > 31:
        return None

    current_year = datetime.now().year % 100

    if is_expiry:
        year = 2000 + yy
    else:
        if yy > current_year:
            year = 1900 + yy
        else:
            year = 2000 + yy

    return f"{year}-{mm:02d}-{dd:02d}"


# =========================
# detect MRZ
# =========================
def detect_mrz(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,7))
    sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21,21))

    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)

    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)

    minVal, maxVal = np.min(gradX), np.max(gradX)
    gradX = (255*((gradX-minVal)/(maxVal-minVal))).astype("uint8")

    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)

    thresh = cv2.threshold(
        gradX,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)

    cnts, _ = cv2.findContours(
        thresh.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    mrz = None

    if len(cnts) > 0:

        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for c in cnts:

            x,y,w,h = cv2.boundingRect(c)

            ar = w / float(h)

            if ar > 5 and w > image.shape[1] * 0.5:

                padding = int(h * 2)

                y1 = max(0, y - padding)
                y2 = min(image.shape[0], y + h + padding)

                mrz = image[y1:y2, x:x+w]

                break

    return mrz


# =========================
# parse MRZ
# =========================
def parse_mrz(lines):

    if len(lines) < 2:
        return None

    l1 = lines[0]
    l2 = lines[1]

    try:

        passport_number = l2[0:9].replace("<", "")
        nationality = l2[10:13]

        dob_raw = l2[13:19]
        gender = l2[20]
        expiry_raw = l2[21:27]

        dob = format_date(dob_raw)
        expiry = format_date(expiry_raw, True)

        name_raw = l1[5:]

        parts = name_raw.split("<<")

        last_name = parts[0].replace("<", " ").strip()

        first_name = ""
        if len(parts) > 1:
            first_name = parts[1].replace("<", " ").strip()

        name = last_name + " " + first_name

        name = re.sub(r'[^A-Z ]', '', name)
        name = " ".join(name.split())

        return {
            "name": name,
            "passportNumber": passport_number,
            "nationality": nationality,
            "dob": dob,
            "gender": gender,
            "expiry": expiry
        }

    except:
        return None


# =========================
# fix OCR error
# =========================
def fix_ocr_line(l):

    l = l.upper()
    l = l.replace(" ", "")

    # lỗi OCR phổ biến
    # l = l.replace("O", "0")
    # l = l.replace("I", "1")
    # l = l.replace("B", "8")
    # l = l.replace("(", "<")
    # l = l.replace("|", "<")

    return l