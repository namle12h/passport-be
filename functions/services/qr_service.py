import cv2
import uuid
import os
from pyzxing import BarCodeReader
import numpy as np




def crop_qr_cccd(img):
    h, w = img.shape[:2]
    return img[0:int(h*0.5), int(w*0.6):w]


def enhance(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    kernel = np.array([[0,-1,0],
                       [-1,5,-1],
                       [0,-1,0]])

    gray = cv2.filter2D(gray, -1, kernel)

    return gray
def decode_zxing(img):

    reader = BarCodeReader()


    temp_path = f"temp_{uuid.uuid4().hex}.png"
    cv2.imwrite(temp_path, img)

    try:
        result = reader.decode(temp_path)

        print("\n===== ZXING RESULT =====")
        print("RAW RESULT:", result)

        if result:
            for item in result:
                print("\n--- ITEM ---")
                print("FORMAT:", item.get("format"))

                raw = item.get("raw")
                print("TYPE RAW:", type(raw))
                print("RAW BYTES:", raw)
                print("RAW REPR:", repr(raw))

                if not raw:
                    continue

                # 🔥 Nếu là bytes
                if isinstance(raw, bytes):

                    # thử UTF-8
                    try:
                        utf8 = raw.decode("utf-8")
                        print("UTF-8:", utf8)
                    except Exception as e:
                        print("UTF-8 FAIL:", e)

                    # thử latin1
                    try:
                        latin1 = raw.decode("latin1")
                        print("LATIN1:", latin1)
                    except Exception as e:
                        print("LATIN1 FAIL:", e)

                    # 👉 convert sang string để xử lý tiếp
                    raw_str = raw.decode("latin1")

                else:
                    raw_str = raw

                # 🔥 thử fix encoding
                try:
                    fixed = raw_str.encode("latin1").decode("utf-8")
                    print("FIXED:", fixed)
                    return fixed
                except Exception as e:
                    print("FIX FAIL:", e)
                    return raw_str

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return None


def detect_qr(img):

    # 🔥 1. crop trước
    roi = crop_qr_cccd(img)

    # 🔥 2. thử luôn (nhanh nhất)
    data = decode_zxing(roi)
    if data:
        return data

    # 🔥 3. enhance rồi thử lại
    roi2 = enhance(roi)
    data = decode_zxing(roi2)
    if data:
        return data

    # 🔥 4. fallback scale lớn hơn
    roi3 = cv2.resize(roi, None, fx=2.5, fy=2.5)
    data = decode_zxing(roi3)

    return data