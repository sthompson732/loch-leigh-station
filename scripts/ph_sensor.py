import os
import time
import geojson
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from utils import (
    load_config,
    setup_logging,
    get_logger,
    now_string,
    today_string,
    append_feature_to_geojson,
    ensure_directory
)

def read_ph():
    config = load_config()
    setup_logging()
    log = get_logger("ph_sensor")

    if not config["sensors"].get("ph", True):
        log.info("pH sensor is disabled in config.")
        return

    try:
        # Setup I2C and ADC
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        chan = AnalogIn(ads, ADS.P0)

        # Read average over a short duration
        samples = []
        for _ in range(10):
            samples.append(chan.voltage)
            time.sleep(0.2)
        avg_voltage = round(sum(samples) / len(samples), 4)
    except Exception as e:
        log.error(f"Failed to read pH sensor: {e}")
        return

    # Basic pH conversion (adjust calibration as needed)
    # Typically: pH = 7 + ((2.5 - voltage) * 3.5)
    ph_value = round(7.0 + ((2.5 - avg_voltage) * 3.5), 2)

    log.info(f"pH reading: {ph_value} (voltage: {avg_voltage}V)")

    station_coords = config["station"]["coordinates"]
    # Create GeoJSON metadata
    feature = geojson.Feature(
        geometry=geojson.Point(tuple(station_coords)),
        properties={
            "type": "ph",
            "timestamp": now_string(),
            "voltage": avg_voltage,
            "ph": ph_value,
            "station": config["station_id"]
        }
    )

    geojson_path = os.path.join(config["paths"]["geojson"], f"ph_{today_string()}.geojson")
    append_feature_to_geojson(feature, geojson_path)
    log.info(f"GeoJSON updated: {geojson_path}")

if __name__ == "__main__":
    read_ph()