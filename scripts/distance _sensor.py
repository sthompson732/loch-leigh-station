import os
import time
import geojson
import RPi.GPIO as GPIO

from utils import (
    load_config,
    setup_logging,
    get_logger,
    now_string,
    today_string,
    append_feature_to_geojson,
    ensure_directory
)

# GPIO setup
TRIG = 17  # BCM pin 17 (physical 11)
ECHO = 27  # BCM pin 27 (physical 13)

def measure_distance_cm():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    GPIO.output(TRIG, False)
    time.sleep(0.5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    timeout = pulse_start + 0.04

    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        pulse_end = time.time()

    GPIO.cleanup()

    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 17150, 2)  # cm
    return distance

def read_distance_sensor():
    config = load_config()
    setup_logging()
    log = get_logger("distance_sensor")

    if not config["sensors"].get("distance", True):
        log.info("Distance sensor disabled in config.")
        return

    try:
        readings = [measure_distance_cm() for _ in range(5)]
        avg_distance = round(sum(readings) / len(readings), 2)
        log.info(f"Avg water distance: {avg_distance} cm")
    except Exception as e:
        log.error(f"Failed to read distance sensor: {e}")
        return
    station_coords = config["station"]["coordinates"]
    # Create GeoJSON metadata
    feature = geojson.Feature(
        geometry=geojson.Point(tuple(station_coords)),
        properties={
            "type": "distance",
            "timestamp": now_string(),
            "distance_cm": avg_distance,
            "station": config["station_id"]
        }
    )

    geojson_path = os.path.join(config["paths"]["geojson"], f"distance_{today_string()}.geojson")
    append_feature_to_geojson(feature, geojson_path)
    log.info(f"GeoJSON updated: {geojson_path}")

if __name__ == "__main__":
    read_distance_sensor()