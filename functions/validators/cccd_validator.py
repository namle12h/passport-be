import re
from datetime import datetime


PROVINCE_CODES = {
    "001": "Ha Noi",
    "002": "Ha Giang",
    "004": "Cao Bang",
    "006": "Bac Kan",
    "008": "Tuyen Quang",
    "010": "Lao Cai",
    "011": "Dien Bien",
    "012": "Lai Chau",
    "014": "Son La",
    "015": "Yen Bai",

    "017": "Hoa Binh",
    "019": "Thai Nguyen",
    "020": "Lang Son",
    "022": "Quang Ninh",
    "024": "Bac Giang",
    "025": "Phu Tho",
    "026": "Vinh Phuc",
    "027": "Bac Ninh",

    "030": "Hai Duong",
    "031": "Hai Phong",
    "033": "Hung Yen",
    "034": "Thai Binh",
    "035": "Ha Nam",
    "036": "Nam Dinh",
    "037": "Ninh Binh",

    "038": "Thanh Hoa",
    "040": "Nghe An",
    "042": "Ha Tinh",
    "044": "Quang Binh",
    "045": "Quang Tri",
    "046": "Thua Thien Hue",

    "048": "Da Nang",
    "049": "Quang Nam",
    "051": "Quang Ngai",
    "052": "Binh Dinh",
    "054": "Phu Yen",
    "056": "Khanh Hoa",
    "058": "Ninh Thuan",
    "060": "Binh Thuan",

    "062": "Kon Tum",
    "064": "Gia Lai",
    "066": "Dak Lak",
    "067": "Dak Nong",
    "068": "Lam Dong",

    "070": "Binh Phuoc",
    "072": "Tay Ninh",
    "074": "Binh Duong",
    "075": "Dong Nai",
    "077": "Ba Ria Vung Tau",
    "079": "Ho Chi Minh",

    "080": "Long An",
    "082": "Tien Giang",
    "083": "Ben Tre",
    "084": "Tra Vinh",
    "086": "Vinh Long",
    "087": "Dong Thap",
    "089": "An Giang",
    "091": "Kien Giang",

    "092": "Can Tho",
    "093": "Hau Giang",
    "094": "Soc Trang",
    "095": "Bac Lieu",
    "096": "Ca Mau"
}


def validate_cccd_number(cccd):

    if not cccd:
        return False

    if not re.match(r'^\d{12}$', cccd):
        return False

    province = cccd[:3]

    if province not in PROVINCE_CODES:
        return False

    try:
        gender_code = int(cccd[3])
    except:
        return False

    if gender_code not in range(0, 6):
        return False

    return True


def parse_birth_year(cccd):

    try:

        gender_code = int(cccd[3])
        year = int(cccd[4:6])

        century = {
            0: 1900,
            1: 1900,
            2: 2000,
            3: 2000,
            4: 2100,
            5: 2100
        }

        birth_year = century[gender_code] + year

        gender = "Nam" if gender_code % 2 == 0 else "Nu"

        return birth_year, gender

    except:
        return None, None


def normalize_date(date_str):

    if not date_str:
        return None

    date_str = date_str.strip()

    try:

        if "-" in date_str:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            return d.strftime("%Y-%m-%d")

        if len(date_str) == 8 and date_str.isdigit():
            d = datetime.strptime(date_str, "%d%m%Y")
            return d.strftime("%Y-%m-%d")

    except:
        return None

    return None


def validate_date(date_str):

    try:

        if "-" in date_str:
            datetime.strptime(date_str, "%Y-%m-%d")

        elif len(date_str) == 8 and date_str.isdigit():
            datetime.strptime(date_str, "%d%m%Y")

        else:
            return False

        return True

    except:
        return False
def validate_cccd_qr(qr_data):

    print("RAW:", qr_data)

    if not qr_data:
        print("FAIL: empty data")
        return None

    if isinstance(qr_data, bytes):
        qr_data = qr_data.decode("utf-8")

    print("DECODED:", qr_data)

    qr_data = str(qr_data).strip()

    if "|" not in qr_data:
        print("FAIL: no | separator")
        return None

    parts = qr_data.split("|")
    print("PARTS:", parts)

    if len(parts) < 6:
        print("FAIL: not enough fields")
        return None

    parts = parts[:6]

    cccd = parts[0].strip()
    name = parts[2].strip()
    dob_raw = parts[3].strip()
    gender = parts[4].strip()
    address = parts[5].strip()

    print("CCCD:", cccd)
    print("NAME:", name)
    print("DOB:", dob_raw)

    if not validate_cccd_number(cccd):
        print("FAIL: CCCD number invalid")
        return None

    if not validate_date(dob_raw):
        print("FAIL: DOB invalid")
        return None

    dob = normalize_date(dob_raw)
    print("DOB normalized:", dob)

    birth_year, gender_from_id = parse_birth_year(cccd)
    print("Birth year from CCCD:", birth_year)

    if dob and birth_year:
        if int(dob[:4]) != birth_year:
            print("FAIL: birth year mismatch")
            return None

    print("VALID CCCD")

    return {
        "id": cccd,
        "name": name,
        "dob": dob,
        "gender": gender,
        "address": address
    }