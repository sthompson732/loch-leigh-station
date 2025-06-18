from scripts.tds_sensor import read_tds
from scripts.utils import setup_logging, get_logger

def test_tds():
    setup_logging()
    log = get_logger("test_tds")
    try:
        print("Attempting to read TDS sensor...")
        read_tds()
        print("PASS: TDS sensor test executed.")
    except Exception as e:
        print(f"FAIL: TDS sensor test failed — {e}")
        log.error(f"TDS test error: {e}")

if __name__ == "__main__":
    test_tds()