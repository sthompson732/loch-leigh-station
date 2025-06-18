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

def read_tds():
    config = load_config()
    setup_logging()
    log = get_logger("tds_sensor")

    if not config["sensors"].get("tds", True):
        log.info("TDS sensor is disabled in config.")
        return

    # Optional temperature correction factor (assumes 25°C baseline)
    water_temp_c = 25.0  # replace with actual sensor reading if wired
    temp_compensation = 1.0 + 0.02 * (water_temp_c - 25.0)

    try:
        # Setup I2C and ADC
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        chan = AnalogIn(ads, ADS.P1)

        # Average 10 samples
        samples = []
        for _ in range(10):
            samples.append(chan.voltage)
            time.sleep(0.2)
        avg_voltage = round(sum(samples) / len(samples), 4)
    except Exception as e:
        log.error(f"Failed to read TDS sensor: {e}")
        return

    # Basic voltage to TDS formula (based on Gravity TDS sensor)
    # EC (ms/cm) = (voltage / 5.0) * 133.42 * (1 + 0.02 * (T - 25))
    ec = (avg_voltage / 5.0) * 133.42 * temp_compensation  # ms/cm
    tds_ppm = round(ec * 0.5 * 1000, 2)  # ppm (500 ppm conversion factor)

    log.info(f"TDS reading: {tds_ppm} ppm (voltage: {avg_voltage}V)")

    station_coords = config["station"]["coordinates"]
    # Create GeoJSON metadata
    feature = geojson.Feature(
        geometry=geojson.Point(tuple(station_coords)),
        properties={
            "type": "tds",
            "timestamp": now_string(),
            "voltage": avg_voltage,
            "ec_ms_cm": round(ec, 4),
            "tds_ppm": tds_ppm,
            "station": config["station_id"]
        }
    )

    geojson_path = os.path.join(config["paths"]["geojson"], f"tds_{today_string()}.geojson")
    append_feature_to_geojson(feature, geojson_path)
    log.info(f"GeoJSON updated: {geojson_path}")

if __name__ == "__main__":
    read_tds()