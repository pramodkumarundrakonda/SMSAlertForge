import glob
import os
import signal
import threading
import time

import pytest
from unittest.mock import patch
from sms_alert_forge.__main__ import read_config, main, setup_logging

config_file_path = 'conf/config.yaml'


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
    main(None, read_config(config_file_path))


@pytest.fixture(autouse=True)
def setup_teardown():
    # Clean up 'logs' directory before each test
    clean_logs_directory()
    yield
    # Clean up 'logs' directory after each test
    clean_logs_directory()


def test_e2e_success_scenario():
    generate_and_save_config_file(3, 3, 0.2, 0.1, 0.1)
    run_main()
    # Find the latest log file
    latest_log_file = get_latest_log_file()

    assert latest_log_file, "No log file found in the 'logs' directory."

    # Read the content of the latest log file for assertions
    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    assert 'Main started.' in log_content.strip(), "Main started message found in the latest log file."


def test_e2e_all_msgs_passed():
    generate_and_save_config_file(100, 5, 0, 0.1, 0.1)
    run_main()
    # Find the latest log file
    latest_log_file = get_latest_log_file()

    assert latest_log_file, "No log file found in the 'logs' directory."

    # Read the content of the latest log file for assertions
    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    assert 'Messages Sent: 100' in log_content.strip()
    assert 'Messages Failed: 0' in log_content.strip()


def test_invalid_config():
    # Generate and save a config file
    generate_and_save_config_file(300, 0.1, 0.2, 0.1, 0.1)

    run_main()

    # Find the latest log file
    latest_log_file = get_latest_log_file()

    assert latest_log_file, "No log file found in the 'logs' directory."

    # Read the content of the latest log file for assertions
    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    # Assert that the error message is present in the output
    assert "Error in main: 'float' object cannot be interpreted as an integer" in log_content.strip()


def test_e2e_failure_high_failure_rate():
    generate_and_save_config_file(10, 3, 1, 0.2, 0.2)
    run_main()

    latest_log_file = get_latest_log_file()
    assert latest_log_file, "No log file found in the 'logs' directory."

    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    assert 'Messages Failed: 10' in log_content.strip()


def test_e2e_failure_zero_messages():
    generate_and_save_config_file(0, 3, 0.2, 0.1, 0.1)
    run_main()

    latest_log_file = get_latest_log_file()
    assert latest_log_file, "No log file found in the 'logs' directory."

    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    assert 'Messages Sent: 0' in log_content.strip()
    assert 'Messages Failed: 0' in log_content.strip()


def send_sigint_thread():
    # Wait for some time before sending the SIGINT signal
    time.sleep(5)

    # Get the process ID of the current application
    current_pid = os.getpid()

    # Send a SIGINT signal to the current process (main thread)
    os.kill(current_pid, signal.SIGINT)


def test_e2e_signal_handler():
    generate_and_save_config_file(1000, 3, 0.2, 0.1, 0.1)
    # Create a thread for sending the SIGINT signal
    sigint_thread = threading.Thread(target=send_sigint_thread)
    sigint_thread.start()
    run_main()
    sigint_thread.join()

    # Find the latest log file
    latest_log_file = get_latest_log_file()

    assert latest_log_file, "No log file found in the 'logs' directory."

    # Read the content of the latest log file for assertions
    with open(latest_log_file, 'r') as log_file:
        log_content = log_file.read()

    assert "Received signal 2. Stopping gracefully." in log_content.strip()
