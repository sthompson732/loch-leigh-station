import os
import json
import time
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from utils import (
    load_config,
    setup_logging,
    get_logger,
    today_string
)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def authenticate_drive(credentials_path):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

def upload_file(drive_service, local_path, folder_id):
    file_metadata = {
        "name": os.path.basename(local_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(local_path, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file.get("id")

def upload_today_files():
    config = load_config()
    setup_logging()
    log = get_logger("upload")

    if not config["upload"].get("enabled", False):
        log.info("Uploads disabled in config.")
        return

    if config["upload"]["method"] != "google_drive":
        log.warning("Only Google Drive upload is supported right now.")
        return

    try:
        credentials_path = config["paths"]["credentials"]
        folder_id = config["upload"]["google_drive"]["folder_id"]
        subfolders = config["upload"]["google_drive"].get("targets", {})
        drive_service = authenticate_drive(credentials_path)
    except Exception as e:
        log.error(f"Authentication failed: {e}")
        return

    base = Path(config["paths"]["data"])
    today = today_string()

    for data_type, rel_path in {
        "geojson": config["paths"]["geojson"],
        "images": config["paths"]["images"],
        "audio": config["paths"]["audio"]
    }.items():
        full_path = Path(rel_path) / today
        if not full_path.exists():
            continue
        for file in full_path.iterdir():
            try:
                target_folder = subfolders.get(data_type, folder_id)
                file_id = upload_file(drive_service, str(file), target_folder)
                log.info(f"Uploaded: {file.name} to folder {target_folder} (ID: {file_id})")
            except Exception as e:
                log.error(f"Failed to upload {file.name}: {e}")

if __name__ == "__main__":
    upload_today_files()