import os
import shutil
from pathlib import Path
from datetime import datetime

from utils import load_config, setup_logging, get_logger, today_string

def find_usb_mount():
    media_root = Path("/media/pi")
    for item in media_root.glob("USB*"):
        if item.is_dir() and os.access(item, os.W_OK):
            return item
    return None

def export_folder(local_dir: Path, usb_dir: Path, log, label: str):
    if not local_dir.exists():
        log.info(f"No {label} to export (not found: {local_dir})")
        return

    dest_dir = usb_dir / "exports" / label / today_string()
    dest_dir.mkdir(parents=True, exist_ok=True)

    for file in local_dir.glob("*"):
        dest_file = dest_dir / file.name
        if not dest_file.exists():
            shutil.copy2(file, dest_file)
            log.info(f"Exported {label}: {file.name}")
        else:
            log.debug(f"Skipped (already exists): {file.name}")

def export_to_usb():
    config = load_config()
    setup_logging()
    log = get_logger("auto_export")

    usb_mount = find_usb_mount()
    if not usb_mount:
        log.warning("No USB drive detected.")
        return

    base_data = Path(config["paths"]["data"])
    today = today_string()

    export_folder(Path(config["paths"]["geojson"]) / today, usb_mount, log, "geojson")
    export_folder(Path(config["paths"]["images"]) / today, usb_mount, log, "images")
    export_folder(Path(config["paths"]["audio"]) / today, usb_mount, log, "audio")

    log.info(f"Export complete: {usb_mount}/exports/*")

if __name__ == "__main__":
    export_to_usb()