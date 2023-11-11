import os
import pytest
import threading
import queue
import time
from unittest.mock import patch
from src.__main__ import read_config, setup_logging, signal_handler, display_fancy_text, main
from src.producer import MessageProducer
from src.sender import MessageSender
from src.progressmonitor import ProgressMonitor

# Use a temporary directory for logs
log_dir = 'tmp_logs'
os.makedirs(log_dir, exist_ok=True)


@pytest.fixture
def config_file_path(tmp_path):
    config_file = tmp_path / 'config.yaml'
    config_content = """
    logging:
        level: INFO
    messages:
        num_messages: 5
    senders:
        num_senders: 3
        failure_rate: 0.2
        mean_processing_time: 0.1
    progress_monitor:
        update_interval: 0.1
    """
    with open(config_file, 'w') as f:
        f.write(config_content)
    return config_file


def test_read_config_valid(config_file_path):
    config = read_config(config_file_path)
    assert 'logging' in config
    assert 'messages' in config
    assert 'senders' in config
    assert 'progress_monitor' in config


def test_read_config_invalid(tmp_path):
    invalid_config_file = tmp_path / 'invalid_config.yaml'
    with open(invalid_config_file, 'w') as f:
        f.write("invalid_yaml: ]")

    with pytest.raises(SystemExit):
        read_config(invalid_config_file)


def test_setup_logging(tmp_path):
    config_file = tmp_path / 'config.yaml'
    config_content = """
    logging:
        level: DEBUG
    """
    with open(config_file, 'w') as f:
        f.write(config_content)

    config = read_config(config_file)
    setup_logging(config)
    log_file_path = os.path.join(log_dir, f"log_{time.strftime('%Y%m%d_%H%M%S')}.log")

    assert os.path.isfile(log_file_path)


def test_signal_handler():
    with patch('os._exit') as mock_exit:
        signal_handler(2, None)
        mock_exit.assert_called_once_with(0)


def test_display_fancy_text(capfd):
    with patch('builtins.open', create=True) as mock_open:
        mock_file = mock_open.return_value
        mock_file.__enter__.return_value.read.return_value = "Fancy Text"

        display_fancy_text(None)
        captured = capfd.readouterr()

        assert "Fancy Text" in captured.out


def test_main(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Main started." in captured.out
    assert "Main completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_main_invalid_config(tmp_path, capfd):
    invalid_config_file = tmp_path / 'invalid_config.yaml'
    with open(invalid_config_file, 'w') as f:
        f.write("invalid_yaml: ]")

    with patch('curses.wrapper'):
        main(None, read_config(invalid_config_file))

    captured = capfd.readouterr()

    assert "Unable to read configurations. Exiting." in captured.out


def test_main_keyboard_interrupt(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Received signal 2. Stopping gracefully." in captured.out
    assert "Main completed." in captured.out


def test_main_exception(config_file_path, capfd):
    with patch('curses.wrapper'):
        with patch('time.sleep', side_effect=Exception("Simulated exception")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Error in main: Simulated exception" in captured.err


def test_main_no_config_file(capfd):
    with patch('curses.wrapper'):
        main(None, None)

    captured = capfd.readouterr()

    assert "Unable to read configurations. Exiting." in captured.out


def test_message_producer_run():
    num_messages = 5
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_senders = 3

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.run()

    assert message_queue.qsize() == num_senders
    for _ in range(num_senders):
        assert message_queue.get() is None


def test_message_sender_run():
    message_queue = queue.Queue()
    failure_rate = 0.2
    mean_processing_time = 0.1
    stop_event = threading.Event()

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.run()

    assert sender.messages_sent == 0
    assert sender.messages_failed == 0
    assert sender.total_processing_time == 0


def test_progress_monitor_run():
    stdscr = None
    update_interval = 0.1
    stop_event = threading.Event()

    sender = MessageSender(queue.Queue(), failure_rate=0.0, mean_processing_time=0.1, stop_event=stop_event)
    progress_monitor = ProgressMonitor(stdscr, [sender], update_interval, stop_event)
    progress_monitor.run()

    assert not progress_monitor.should_terminate.is_set()


def test_progress_monitor_stop():
    stdscr = None
    update_interval = 0.1
    stop_event = threading.Event()

    sender = MessageSender(queue.Queue(), failure_rate=0.0, mean_processing_time=0.1, stop_event=stop_event)
    progress_monitor = ProgressMonitor(stdscr, [sender], update_interval, stop_event)
    progress_monitor.stop()

    assert progress_monitor.should_terminate.is_set()
