
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Lấy từ biến môi trường thay vì hardcode
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
FOLDER_ID = os.getenv("FOLDER_ID")


def get_drive_service():

    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )

    return build("drive", "v3", credentials=creds)


def upload_to_drive(filepath, filename):

    drive_service = get_drive_service()

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }

    media = MediaFileUpload(filepath, mimetype="image/jpeg")

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    drive_service.permissions().create(
        fileId=file.get("id"),
        body={
            "type": "anyone",
            "role": "reader"
        }
    ).execute()

    return file.get("id")