
# Loch Leigh Station

Welcome to **Loch Leigh Station** - a modular, solar-capable, Raspberry Pi-powered lake monitoring system designed for Loch Leigh in **West Leigh II** and adaptable to small-scale ecological projects anywhere.

This system was built to be:
- **Modular and low-maintenance**
- **Offline-first**, supporting USB sneakernet or internet upload
- **Scientifically meaningful**, collecting robust water and environmental data
- **Community-accessible**, designed for smart, curious non-technical users
- **GIS-native**, feeding directly into QGIS projects

---

## Table of Contents
1. Project Overview
2. Hardware Architecture
3. Software Overview
4. Installation
5. Directory Structure
6. Sensor Descriptions
7. Scheduling & Automation
8. Offline & USB Export Support
9. Google Drive Integration
10. Testing Utilities
11. QGIS Integration
12. Future Enhancements
13. Troubleshooting & Support

---

## Project Overview
**Loch Leigh Station** continuously captures and stores:
- Water temperature
- pH
- TDS (Total Dissolved Solids)
- Ultrasonic water level
- Daily camera snapshots
- 5-minute birdsong audio recordings

Each sensor generates timestamped, GIS-compatible GeoJSON files, optionally uploading to a shared Google Drive, or copying to USB for manual transfer.

---

## Hardware Architecture
- Raspberry Pi 3 (Raspberry Pi OS Lite 32-bit)
- DS18B20 waterproof temperature probe (1-Wire)
- CQRobot Analog pH Sensor via ADS1115 ADC (I2C)
- CQRobot TDS Sensor via ADS1115 (I2C)
- JSN-SR04T waterproof ultrasonic distance sensor (GPIO)
- USB Microphone (for birdsong)
- Camera (PiCamera2) for lake timelapse
- Power: initially wall plug, later solar + battery

---

## Software Overview
- Language: Python 3.11
- Environment: venv in `lochleigh_env/`
- Logging: YAML-based to `data/logs/`
- Scheduler: single smart `scheduler.py` cron-driven
- File Outputs: GeoJSON, WAV, JPG â€” one folder per day
- Upload: Google Drive via service account
- Sneakernet: USB auto-export supported
- Fully cron-compatible, runs headless

---

## Installation

### 1. Flash Pi OS Lite and boot Pi
- Download Raspberry Pi OS Lite (32-bit)
- Flash to SD card using Raspberry Pi Imager or Balena Etcher
- Boot and expand filesystem

### 2. Clone or copy this repo to `/home/pi/loch_leigh_station/`

### 3. Run setup:
```bash
cd ~/loch_leigh_station
chmod +x setup.sh
./setup.sh
sudo reboot
```

This:
- Installs Python environment
- Installs all dependencies
- Sets up directory structure
- Configures cron
- Enables 1-Wire and I2C

---

## Directory Structure

```
loch_leigh_station/
 config/             -  config.json, logging.yaml
 crontab/            -  crontab.txt
 data/
 audio/          -  WAVs (recorded daily)
 geojson/        -  Per-sensor daily logs
 images/         -  Photos (twice daily)
 logs/           -  station.log, upload.log, etc.
 exports/            -  USB-bound exports
 scripts/            -  All sensors + upload/scheduler
 usb_mount/          -  auto_export.py
 tests/              -  test_*.py
 setup.sh            -  Installs all infra
 requirements.txt    -  Frozen dependencies
```

---

## Sensor Descriptions

- `camera.py`: captures 2 JPGs per day
- `audio_recorder.py`: records 5-min WAV clips, 2x per day
- `temp_sensor.py`: reads DS18B20, outputs GeoJSON
- `ph_sensor.py`: reads analog pH via ADS1115
- `tds_sensor.py`: same as above, different channel
- `distance_sensor.py`: ultrasonic level detection

Each sensor appends daily GeoJSON output to:
`data/geojson/{sensor}_{YYYY-MM-DD}.geojson`

---

## Scheduling & Automation

All scheduling is handled by `scheduler.py` based on `config.json`.

- The `scheduler.py` script runs once per minute via `cron`
- It checks the configured times for each sensor (e.g. snapshot, audio)
- It also runs interval-based sensors (e.g. temp, TDS, pH) every N minutes
- Because `scheduler.py` defers logic to `config.json`, you can change behavior without editing any code

Additional scheduled jobs:

- `upload.py`: triggered once daily to sync data to Google Drive (if enabled)
- `auto_export.py`: copies daily data to USB if present â€” also cron-triggered

---

## Offline & USB Export Support

- If no internet, recordings and data are copied to USB
- Plug in a drive (`/media/pi/USB*`), run `auto_export.py`
- USB layout:

```
/exports/
 audio/YYYY-MM-DD/
 geojson/YYYY-MM-DD/
 images/YYYY-MM-DD/
```

---

## Google Drive Integration

- Upload enabled via `upload.py` + service account
- Requires `credentials.json` (not in repo)
- Configure target folder IDs in `config.json`
- Auto uploads:
  - Daily GeoJSON
  - Birdsong WAVs
  - Lake snapshots

---

## Testing Utilities

Each `test_*.py` script in `tests/`:
- Loads and runs a single module
- Verifies real hardware I/O
- Can be run individually or via batch script

Test scripts:
```
test_camera.py
test_ph_sensor.py
test_tds_sensor.py
test_utils.py
```

---

## QGIS Integration

- All output is in clean GeoJSON format
- Each feature includes: `type`, `timestamp`, `value`, `station`, and `filename`
- Directly importable to **QField** or desktop QGIS
- Styling handled via `.qml` layer styles (external)
- Exported GeoJSON files can also be shared over USB or Google Drive

---

## Future Enhancements

- Add dissolved oxygen sensor (ADC channel available)
- Switch to solar + battery, monitor voltage
- Add RTC for more accurate scheduling
- Install Merlin/BirdNet model on external machine for classification
- Build live dashboard via Deck.gl
- Add signal health / noise detection to audio pipeline

---

## Troubleshooting & Support

- All logs go to `data/logs/`
- Use `tail -f` to watch sensor output live
- Run individual `test_*.py` scripts if a sensor misbehaves
- Check GPIO wiring, power voltage, and config toggles if issues persist
- Logs will indicate skipped sensors if they are disabled in `config.json`

---
