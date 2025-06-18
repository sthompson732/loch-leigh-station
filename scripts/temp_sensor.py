import glob
import os
import time
import geojson

from utils import (
    load_config,
    setup_logging,
    get_logger,
    now_string,
    today_string,
    append_feature_to_geojson,
)

def read_temp_raw(device_file):
    try:
        with open(device_file, "r") as f:
            lines = f.readlines()
        return lines
    except Exception as e:
        return None

def parse_temp_c(device_file):
    lines = read_temp_raw(device_file)
    if not lines or "YES" not in lines[0]:
        return None
    temp_str = lines[1].split("t=")[-1].strip()
    return float(temp_str) / 1000.0

def read_temp_sensor():
    config = load_config()
    setup_logging()
    log = get_logger("temp_sensor")

    if not config["sensors"].get("temp", True):
        log.info("Temp sensor is disabled in config.")
        return

    base_dir = "/sys/bus/w1/devices/"
    device_folders = glob.glob(base_dir + "28*")  # DS18B20 starts with '28'

    if not device_folders:
        log.error("No DS18B20 sensor found.")
        return

    device_file = os.path.join(device_folders[0], "w1_slave")
    temp_c = parse_temp_c(device_file)

    if temp_c is None:
        log.error("Failed to read temperature.")
        return

    temp_f = round(temp_c * 9.0 / 5.0 + 32.0, 2)
    temp_c = round(temp_c, 2)
    log.info(f"Temp reading: {temp_c}°C / {temp_f}°F")

    station_coords = config["station"]["coordinates"]
    # Create GeoJSON metadata
    feature = geojson.Feature(
        geometry=geojson.Point(tuple(station_coords)),
        properties={
            "type": "temperature",
            "timestamp": now_string(),
            "temp_c": temp_c,
            "temp_f": temp_f,
            "station": config["station_id"]
        }
    )

    geojson_dir = config["paths"]["geojson"]
    geojson_path = os.path.join(geojson_dir, f"temp_{today_string()}.geojson")
    append_feature_to_geojson(feature, geojson_path)
    log.info(f"GeoJSON updated: {geojson_path}")

if __name__ == "__main__":
    read_temp_sensor()