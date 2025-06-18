from scripts.utils import load_config, setup_logging, get_logger
import os
from picamera2 import Picamera2
from datetime import datetime

def test_camera():
    setup_logging()
    log = get_logger("test_camera")

    try:
        picam = Picamera2()
        picam.start()
        filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        picam.capture_file(filename)
        picam.close()
        if os.path.exists(filename):
            print(f"PASS: Camera captured image: {filename}")
            os.remove(filename)
        else:
            print("FAIL: Camera image not saved.")
    except Exception as e:
        print(f"FAIL: Camera test failed — {e}")
        log.error(f"Camera test error: {e}")

if __name__ == "__main__":
    test_camera()