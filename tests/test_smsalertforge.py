import glob
import os
import signal
import threading
import time
import warnings

import pytest
from unittest.mock import patch
from sms_alert_forge.__main__ import read_config, main, setup_logging

config_file_path = 'tests/conf/config.yaml'


def generate_and_save_config_file(num_messages, num_senders, failure_rate, mean_processing_time, update_interval):
    config_content = f"""
        logging:
            level: INFO
            to_console: false
            to_file: true
        messages:
            num_messages: {num_messages}
        senders:
            num_senders: {num_senders}
            failure_rate: {failure_rate}
            mean_processing_time: {mean_processing_time}
        progress_monitor:
            update_interval: {update_interval}
        """
    with open(config_file_path, 'w') as f:
        f.write(config_content)


def get_latest_log_file():
    log_dir = 'logs'
    log_files = glob.glob(os.path.join(log_dir, 'log*.log'))
    return max(log_files, key=os.path.getctime) if log_files else None


def clean_logs_directory():
    # Remove all files in the 'logs' directory
    log_dir = 'logs'
    for file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)



def run_main():
    setup_logging(read_config(config_file_path))
    sms_report = main(None, read_config(config_file_path))
    return sms_report


@pytest.fixture(autouse=True)
def setup_teardown():
    # Clean up 'logs' directory before each test
    clean_logs_directory()
    yield
    # Clean up 'logs' directory after each test
    clean_logs_directory()


@pytest.fixture(autouse=True)
def suppress_warnings(request):
    # Suppress PytestUnhandledThreadExceptionWarning
    warnings.filterwarnings("ignore", category=pytest.PytestUnhandledThreadExceptionWarning)

    # Yield control back to the test function
    yield

    # Reset warnings filters after the test
    warnings.resetwarnings()


def test_e2e_success_scenario():
    generate_and_save_config_file(3, 3, 0.2, 0.1, 0.1)
    sms_report = run_main()
    # Find the latest log file
    latest_log_file = get_latest_log_file()

    assert latest_log_file, "No log file found in the 'logs' directory."

    # Read the content of the latest log file for assertions
    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    assert 'Main completed.' in log_content.strip(), "Main completed message found in the latest log file."


def test_invalid_config():
    # Generate and save a config file
    generate_and_save_config_file(300, 0.1, 0.2, 0.1, 0.1)

    with pytest.raises(TypeError, match="'float' object cannot be interpreted as an integer"):
        run_main()


def test_e2e_failure_zero_messages():
    generate_and_save_config_file(0, 3, 0.2, 0.1, 0.1)
    run_main()

    latest_log_file = get_latest_log_file()
    assert latest_log_file, "No log file found in the 'logs' directory."

    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    assert 'Messages Sent: 0' in log_content.strip()
    assert 'Messages Failed: 0' in log_content.strip()
