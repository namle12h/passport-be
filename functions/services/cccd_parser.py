def parse_cccd_qr(data):

    if not data:
        return None

    if isinstance(data, bytes):
        data = data.decode("utf-8")

    data = str(data)

    parts = data.split("|")

    if len(parts) < 6:
        return {
            "raw": data
        }

    return {
        "id": parts[0],
        "cmnd_old": parts[1],
        "name": parts[2],
        "dob": parts[3],
        "gender": parts[4],
        "address": parts[5]
    }