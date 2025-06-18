import os
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write
import geojson

from utils import (
    load_config,
    setup_logging,
    get_logger,
    now_string,
    today_string,
    filename_timestamp,
    append_feature_to_geojson,
    ensure_directory
)

def record_audio():
    config = load_config()
    setup_logging()
    log = get_logger("audio_recorder")

    if not config["sensors"].get("audio", True):
        log.info("Audio recording skipped (disabled in config).")
        return

    duration = config["schedule"].get("audio_duration_sec", 300)
    sample_rate = 44100
    channels = 1

    timestamp = filename_timestamp()
    audio_dir = os.path.join(config["paths"]["audio"], today_string())
    ensure_directory(audio_dir)

    filename = f"birdsong_{timestamp}.wav"
    filepath = os.path.join(audio_dir, filename)

    try:
        log.info(f"Recording audio: {filepath} ({duration}s)")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels)
        sd.wait()
        write(filepath, sample_rate, audio)
        log.info(f"Saved: {filepath}")
    except Exception as e:
        log.error(f"Audio recording failed: {e}")
        return

    station_coords = config["station"]["coordinates"]
    # Create GeoJSON metadata
    feature = geojson.Feature(
        geometry=geojson.Point(tuple(station_coords)),
        properties={
            "type": "audio",
            "timestamp": now_string(),
            "filename": filename,
            "duration_sec": duration,
            "station": config["station_id"]
        }
    )

    geojson_path = os.path.join(config["paths"]["geojson"], f"audio_{today_string()}.geojson")
    append_feature_to_geojson(feature, geojson_path)
    log.info(f"GeoJSON updated: {geojson_path}")

if __name__ == "__main__":
    record_audio()