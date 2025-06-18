import os
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2
import geojson

from utils import (
    load_config,
    setup_logging,
    get_logger,
    now_string,
    today_string,
    filename_timestamp,
    build_output_path,
    append_feature_to_geojson,
)

def capture_image():
    config = load_config()
    setup_logging()
    log = get_logger("camera")

    if not config["sensors"].get("camera", True):
        log.info("Camera capture skipped (disabled in config).")
        return

    output_dir = config["paths"]["images"]
    geojson_dir = config["paths"]["geojson"]

    # Ensure dated subdir exists
    today_dir = os.path.join(output_dir, today_string())
    Path(today_dir).mkdir(parents=True, exist_ok=True)

    # Set filename
    timestamp = filename_timestamp()
    image_path = os.path.join(today_dir, f"lake_{timestamp}.jpg")

    # Initialize camera
    try:
        picam = Picamera2()
        picam.start()
        picam.capture_file(image_path)
        picam.close()
        log.info(f"Image captured: {image_path}")
    except Exception as e:
        log.error(f"Camera error: {e}")
        return

    station_coords = config["station"]["coordinates"]
    # Create GeoJSON metadata
    feature = geojson.Feature(
        geometry=geojson.Point(tuple(station_coords)),
        properties={
            "type": "photo",
            "timestamp": now_string(),
            "filename": os.path.basename(image_path),
            "path": image_path,
            "station": config["station_id"]
        }
    )

    geojson_path = os.path.join(geojson_dir, f"camera_{today_string()}.geojson")
    append_feature_to_geojson(feature, geojson_path)
    log.info(f"GeoJSON updated: {geojson_path}")


if __name__ == "__main__":
    capture_image()