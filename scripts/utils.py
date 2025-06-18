import os
import json
import yaml
import logging
import logging.config
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union
import geojson


# --------------------------
# Config + Logging Utilities
# --------------------------

def load_config(config_path: str = "config/config.json") -> Dict[str, Any]:
    with open(os.path.join(os.path.dirname(__file__), "..", config_path), "r") as f:
        return json.load(f)


def setup_logging(logging_config_path: str = "config/logging.yaml") -> None:
    with open(os.path.join(os.path.dirname(__file__), "..", logging_config_path), "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


# --------------------------
# Time Utilities
# --------------------------

def now_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_string() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def filename_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# --------------------------
# File Output Helpers
# --------------------------

def ensure_directory(path: Union[str, Path]) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def save_geojson(data: dict, output_path: Union[str, Path]) -> None:
    ensure_directory(Path(output_path).parent)
    with open(output_path, "w") as f:
        geojson.dump(data, f, indent=2)


def append_feature_to_geojson(feature: geojson.Feature, filepath: str) -> None:
    ensure_directory(Path(filepath).parent)
    if Path(filepath).exists():
        with open(filepath, "r") as f:
            gj = geojson.load(f)
        gj["features"].append(feature)
    else:
        gj = geojson.FeatureCollection([feature])

    with open(filepath, "w") as f:
        geojson.dump(gj, f, indent=2)


# --------------------------
# Log + Path Utilities
# --------------------------

def build_output_path(base: str, kind: str, ext: str) -> str:
    timestamp = filename_timestamp()
    return f"{base}/{today_string()}/{kind}_{timestamp}.{ext}"


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
