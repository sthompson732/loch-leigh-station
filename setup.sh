#!/bin/bash

set -e  # exit on any failure

echo ">> Loch Leigh Station Setup Starting..."

BASE_DIR="/home/pi/loch_leigh_station"
VENV_DIR="$BASE_DIR/lochleigh_env"
CRON_SRC="$BASE_DIR/crontab/crontab.txt"
LOG_DIR="$BASE_DIR/data/logs"

# 1. Create Python virtual environment
echo ">> Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# 2. Upgrade pip and install all Python requirements
echo ">> Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r "$BASE_DIR/requirements.txt"

# 3. Create required folders
echo ">> Creating data directories..."
mkdir -p \
  "$BASE_DIR/data/geojson" \
  "$BASE_DIR/data/audio" \
  "$BASE_DIR/data/images" \
  "$LOG_DIR" \
  "$BASE_DIR/exports/ready"

# 4. Install crontab
echo ">> Installing crontab..."
crontab "$CRON_SRC"

# 5. Enable I2C and 1-Wire in /boot/config.txt (safe append)
echo ">> Enabling I2C and 1-Wire..."
CONFIG="/boot/config.txt"
grep -qxF 'dtparam=i2c_arm=on' $CONFIG || echo 'dtparam=i2c_arm=on' | sudo tee -a $CONFIG
grep -qxF 'dtoverlay=w1-gpio' $CONFIG || echo 'dtoverlay=w1-gpio' | sudo tee -a $CONFIG

# 6. Give permission to use I2C and GPIO
echo ">> Adding pi to I2C and SPI groups..."
sudo usermod -aG i2c pi
sudo usermod -aG gpio pi
sudo usermod -aG spi pi

# 7. Touch a first-run log file
echo ">> Initializing log file..."
touch "$LOG_DIR/station.log"
chmod 666 "$LOG_DIR/station.log"

# 8. Done
echo ">> Loch Leigh Station setup complete."
echo ">> Reboot your Pi to apply hardware permissions."

exit 0