from scripts.utils import (
    now_string,
    today_string,
    filename_timestamp,
    build_output_path,
    get_logger,
    setup_logging
)

def test_utils():
    setup_logging()
    log = get_logger("test_utils")

    try:
        print("Testing time utilities...")
        print(f"NOW: {now_string()}")
        print(f"TODAY: {today_string()}")
        print(f"STAMP: {filename_timestamp()}")
        print(f"Path: {build_output_path('/tmp', 'test', 'txt')}")
        print("PASS: utils.py functional")
    except Exception as e:
        print(f"FAIL: utils.py test failed — {e}")
        log.error(f"Utils test error: {e}")

if __name__ == "__main__":
    test_utils()