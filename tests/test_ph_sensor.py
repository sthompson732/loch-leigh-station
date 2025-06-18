from scripts.ph_sensor import read_ph
from scripts.utils import setup_logging, get_logger

def test_ph():
    setup_logging()
    log = get_logger("test_ph")
    try:
        print("Attempting to read pH sensor...")
        read_ph()
        print("PASS: pH sensor test executed.")
    except Exception as e:
        print(f"FAIL: pH sensor test failed — {e}")
        log.error(f"PH test error: {e}")

if __name__ == "__main__":
    test_ph()