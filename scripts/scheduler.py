import os
import subprocess
from datetime import datetime
from utils import load_config, setup_logging, get_logger

def scheduler_main():
    config = load_config()
    setup_logging()
    log = get_logger("scheduler")

    now = datetime.now()
    current_time = now.strftime("%H:%M")

    base_path = config["paths"]["base"]
    active_sensors = config.get("sensors", {})

    # Trigger snapshot if now matches any configured time
    if current_time in config["schedule"].get("snapshot_times", []):
        if active_sensors.get("camera", False):
            log.info("Scheduled: Camera snapshot")
            subprocess.run(["python3", f"{base_path}/scripts/camera.py"])

    # Trigger audio recording
    if current_time in config["schedule"].get("audio_record_times", []):
        if active_sensors.get("audio", False):
            log.info("Scheduled: Audio recording")
            subprocess.run(["python3", f"{base_path}/scripts/audio_recorder.py"])

    # Trigger sensor polling by interval
    interval = config["schedule"].get("sensor_poll_interval_min", 60)
    if now.minute % interval == 0:
        for sensor_script, enabled in {
            "temp_sensor.py": active_sensors.get("temp", False),
            "ph_sensor.py": active_sensors.get("ph", False),
            "tds_sensor.py": active_sensors.get("tds", False),
            "distance_sensor.py": active_sensors.get("distance", False),
        }.items():
            if enabled:
                log.info(f"Scheduled: {sensor_script}")
                subprocess.run(["python3", f"{base_path}/scripts/{sensor_script}"])

if __name__ == "__main__":
    scheduler_main()