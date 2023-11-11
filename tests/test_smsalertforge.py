import curses
import io
import os
import pytest
from unittest.mock import patch
from src.__main__ import read_config, main
from src.producer import MessageProducer
from src.progressmonitor import ProgressMonitor
from src.sender import MessageSender

# Use a temporary directory for logs
log_dir = 'tmp_logs'
os.makedirs(log_dir, exist_ok=True)


@pytest.fixture
def config_file_path(tmp_path):
    config_file = tmp_path / 'config.yaml'
    config_content = """
    logging:
        level: INFO
        to_console: true
        to_file: false  
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


def test_e2e_success_scenario(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        main(None, read_config(config_file_path))

    captured = capfd.readouterr()
    print("Captured Output:", captured.out)

    assert "Main started." in captured.out
    assert "Main completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_e2e_keyboard_interrupt(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Received signal 2. Stopping gracefully." in captured.out
    assert "Main completed." in captured.out


def test_e2e_exception(config_file_path, capfd):
    with patch('curses.wrapper'):
        with patch('time.sleep', side_effect=Exception("Simulated exception")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Error in main: Simulated exception" in captured.err


def test_e2e_message_sending_failure(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageSender, 'run', side_effect=Exception("Simulated sender failure")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "MessageSender started." in captured.out
    assert "Error in MessageSender: Simulated sender failure" in captured.err
    assert "MessageSender completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_e2e_producer_exception(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=Exception("Simulated producer exception")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "MessageProducer started." in captured.out
    assert "Error in MessageProducer: Simulated producer exception" in captured.err
    assert "MessageProducer completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_e2e_progress_monitor_failure(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(ProgressMonitor, 'run', side_effect=Exception("Simulated progress monitor failure")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "ProgressMonitor started." in captured.out
    assert "Error in ProgressMonitor: Simulated progress monitor failure" in captured.err
    assert "ProgressMonitor completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_e2e_keyboard_interrupt_during_execution(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('time.sleep', side_effect=[None, KeyboardInterrupt]):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Received signal 2. Stopping gracefully." in captured.out
    assert "Main completed." in captured.out


def test_e2e_invalid_config(tmp_path, capfd):
    invalid_config_file = tmp_path / 'invalid_config.yaml'
    with open(invalid_config_file, 'w') as f:
        f.write("invalid_yaml: ]")

    with patch('curses.wrapper'):
        main(None, read_config(invalid_config_file))

    captured = capfd.readouterr()

    assert "Unable to read configurations. Exiting." in captured.out


def test_e2e_message_producer_exception(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=Exception("Simulated producer exception")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "MessageProducer started." in captured.out
    assert "Error in MessageProducer: Simulated producer exception" in captured.err
    assert "MessageProducer completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_e2e_message_producer_keyboard_interrupt(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Received signal 2. Stopping gracefully." in captured.out
    assert "MessageProducer completed." in captured.out


def test_e2e_message_sender_keyboard_interrupt(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageSender, 'run', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Received signal 2. Stopping gracefully." in captured.out
    assert "MessageSender completed." in captured.out


def test_e2e_message_sender_exception(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageSender, 'run', side_effect=Exception("Simulated sender exception")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "MessageSender started." in captured.out
    assert "Error in MessageSender: Simulated sender exception" in captured.err
    assert "MessageSender completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_e2e_progress_monitor_keyboard_interrupt(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(ProgressMonitor, 'run', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "Received signal 2. Stopping gracefully." in captured.out
    assert "ProgressMonitor completed." in captured.out


def test_e2e_progress_monitor_exception(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(ProgressMonitor, 'run', side_effect=Exception("Simulated progress monitor exception")):
            main(None, read_config(config_file_path))

    captured = capfd.readouterr()

    assert "ProgressMonitor started." in captured.out
    assert "Error in ProgressMonitor: Simulated progress monitor exception" in captured.err
    assert "ProgressMonitor completed." in captured.out
    assert "Press 'q' to exit." in captured.out


def test_e2e_multiple_producers_and_senders(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run') as mock_producer_run, \
                patch.object(MessageSender, 'run') as mock_sender_run:
            main(None, read_config(config_file_path))

    assert mock_producer_run.call_count == 1  # Single producer thread
    assert mock_sender_run.call_count == 3  # Three sender threads


def test_e2e_progress_monitor_updates(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(ProgressMonitor, 'run') as mock_progress_monitor_run:
            main(None, read_config(config_file_path))

    assert mock_progress_monitor_run.call_count == 1  # Progress monitor thread


def test_e2e_producer_stops_early(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('time.sleep') as mock_sleep, \
                patch.object(MessageProducer, 'run', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    assert mock_sleep.call_count == 1  # Sleep before starting the simulation
    assert mock_sleep.call_args[0][0] == 2  # Sleep for 2 seconds
    assert "MessageProducer started." in capfd.readouterr().out
    assert "Received signal 2. Stopping gracefully." in capfd.readouterr().out
    assert "MessageProducer completed." in capfd.readouterr().out


def test_e2e_sender_stops_early(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('time.sleep', side_effect=[None, KeyboardInterrupt]), \
                patch.object(MessageSender, 'run', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    assert "MessageSender started." in capfd.readouterr().out
    assert "Received signal 2. Stopping gracefully." in capfd.readouterr().out
    assert "MessageSender completed." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_progress_monitor_stops_early(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('time.sleep', side_effect=[None, KeyboardInterrupt]), \
                patch.object(ProgressMonitor, 'run', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    assert "ProgressMonitor started." in capfd.readouterr().out
    assert "Received signal 2. Stopping gracefully." in capfd.readouterr().out
    assert "ProgressMonitor completed." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_producer_exception_before_sending(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=Exception("Producer exception")):
            main(None, read_config(config_file_path))

    assert "MessageProducer started." in capfd.readouterr().out
    assert "Error in MessageProducer: Producer exception" in capfd.readouterr().err
    assert "MessageProducer completed." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_producer_exception_after_sending(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=[None, Exception("Producer exception")]):
            main(None, read_config(config_file_path))

    assert "MessageProducer started." in capfd.readouterr().out
    assert "MessageProducer completed." in capfd.readouterr().out
    assert "Error in MessageProducer: Producer exception" in capfd.readouterr().err
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_sender_exception_before_processing(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageSender, 'run', side_effect=Exception("Sender exception")):
            main(None, read_config(config_file_path))

    assert "MessageSender started." in capfd.readouterr().out
    assert "Error in MessageSender: Sender exception" in capfd.readouterr().err
    assert "MessageSender completed." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_sender_exception_after_processing(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageSender, 'run', side_effect=[None, Exception("Sender exception")]):
            main(None, read_config(config_file_path))

    assert "MessageSender started." in capfd.readouterr().out
    assert "MessageSender completed." in capfd.readouterr().out
    assert "Error in MessageSender: Sender exception" in capfd.readouterr().err
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_progress_monitor_exception_before_monitoring(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(ProgressMonitor, 'run', side_effect=Exception("Progress monitor exception")):
            main(None, read_config(config_file_path))

    assert "ProgressMonitor started." in capfd.readouterr().out
    assert "Error in ProgressMonitor: Progress monitor exception" in capfd.readouterr().err
    assert "ProgressMonitor completed." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_progress_monitor_exception_after_monitoring(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(ProgressMonitor, 'run', side_effect=[None, Exception("Progress monitor exception")]):
            main(None, read_config(config_file_path))

    assert "ProgressMonitor started." in capfd.readouterr().out
    assert "ProgressMonitor completed." in capfd.readouterr().out
    assert "Error in ProgressMonitor: Progress monitor exception" in capfd.readouterr().err
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_multiple_exceptions(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=Exception("Producer exception")), \
                patch.object(MessageSender, 'run', side_effect=Exception("Sender exception")), \
                patch.object(ProgressMonitor, 'run', side_effect=Exception("Progress monitor exception")):
            main(None, read_config(config_file_path))

    assert "MessageProducer started." in capfd.readouterr().out
    assert "Error in MessageProducer: Producer exception" in capfd.readouterr().err
    assert "MessageSender started." in capfd.readouterr().out
    assert "Error in MessageSender: Sender exception" in capfd.readouterr().err
    assert "ProgressMonitor started." in capfd.readouterr().out
    assert "Error in ProgressMonitor: Progress monitor exception" in capfd.readouterr().err
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_keyboard_interrupt_during_run(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    assert "MessageProducer started." in capfd.readouterr().out
    assert "Received signal 2. Stopping gracefully." in capfd.readouterr().out
    assert "MessageProducer completed." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_keyboard_interrupt_before_run(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            main(None, read_config(config_file_path))

    assert "Received signal 2. Stopping gracefully." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_invalid_config_file(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('smsalertforge.read_config', side_effect=FileNotFoundError):
            main(None, read_config(config_file_path))

    assert "Config file 'config.yaml' not found. Exiting." in capfd.readouterr().err


def test_e2e_invalid_yaml_format(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('smsalertforge.read_config', side_effect=yaml.YAMLError("Simulated YAML error")):
            main(None, read_config(config_file_path))

    assert "Error reading YAML from 'config.yaml': Simulated YAML error. Exiting." in capfd.readouterr().err


def test_e2e_empty_config_file(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('smsalertforge.read_config',
                   side_effect=[{'logging': {'level': 'INFO'}, 'messages': {}, 'senders': {}, 'progress_monitor': {}}]):
            main(None, read_config(config_file_path))

    assert "One or more required fields are empty in the configuration. Exiting." in capfd.readouterr().err


def test_e2e_fancy_text_display_error(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('smsalertforge.display_fancy_text', side_effect=Exception("Simulated fancy text display error")):
            main(None, read_config(config_file_path))

    assert "Error reading ASCII art file: Simulated fancy text display error" in capfd.readouterr().err


def test_e2e_no_fancy_text_file(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch('builtins.open', side_effect=FileNotFoundError):
            main(None, read_config(config_file_path))

    assert "ASCII art file 'banner.txt' not found." in capfd.readouterr().err


def test_e2e_message_queue_exception(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'run', side_effect=Exception("Simulated message queue exception")):
            main(None, read_config(config_file_path))

    assert "MessageProducer started." in capfd.readouterr().out
    assert "Error in MessageProducer: Simulated message queue exception" in capfd.readouterr().err
    assert "MessageProducer completed." in capfd.readouterr().out
    assert "Press 'q' to exit." in capfd.readouterr().out


def test_e2e_producer_join_timeout(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageProducer, 'join', side_effect=TimeoutError("Simulated join timeout")):
            main(None, read_config(config_file_path))

    assert "Error in main: Simulated join timeout" in capfd.readouterr().err


def test_e2e_sender_join_timeout(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(MessageSender, 'join', side_effect=TimeoutError("Simulated join timeout")):
            main(None, read_config(config_file_path))

    assert "Error in main: Simulated join timeout" in capfd.readouterr().err


def test_e2e_progress_monitor_join_timeout(config_file_path, capfd):
    with patch('curses.wrapper') as mock_curses_wrapper:
        with patch.object(ProgressMonitor, 'join', side_effect=TimeoutError("Simulated join timeout")):
            main(None, read_config(config_file_path))

    assert "Error in main: Simulated join timeout" in capfd.readouterr().err


def test_e2e_success_scenario(capfd):
    def display_callback(msg):
        print(msg)

    # Redirect stdout to capture printed messages
    with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
        # Call the main function with a mocked curses window
        stdscr = main(curses.initscr(), read_config(config_file_path), output_callback=display_callback)

    captured = capfd.readouterr()

    # Assertions for log messages
    assert "Main started." in mock_stdout.getvalue()
    assert "Main completed." in mock_stdout.getvalue()
    assert "Press 'q' to exit." in mock_stdout.getvalue()

    # Additional assertions for captured curses output
    assert "Elapsed Time" in captured.out
    assert "Messages Sent" in captured.out
    assert "Messages Failed" in captured.out
    assert "Average Time per Message" in captured.out
