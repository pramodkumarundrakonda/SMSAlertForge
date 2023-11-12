import threading
import queue
import time

from sms_alert_forge.producer import MessageProducer
from sms_alert_forge.progressmonitor import ProgressMonitor
from sms_alert_forge.sender import MessageSender


def test_progress_monitor_success():
    stdscr = None  # Use None for the curses window object
    update_interval = 0.1
    stop_event = threading.Event()

    # Create a list of sender threads
    senders = []
    for _ in range(3):
        message_queue = queue.Queue()
        sender = MessageSender(message_queue, failure_rate=0.0, mean_processing_time=0.1, stop_event=stop_event)
        senders.append(sender)

    progress_monitor = ProgressMonitor(stdscr, senders, update_interval, stop_event)
    progress_monitor.start()

    # Enqueue a message for each sender
    for sender in senders:
        sender.start()
        sender.message_queue.put(('1234567890', 'Test message'))

    # Wait for the senders to process the messages
    for sender in senders:
        sender.join()

    # Signal the stop event
    stop_event.set()

    # Wait for the progress monitor to stop
    progress_monitor.join()

    # Ensure the progress monitor stops gracefully
    assert not progress_monitor.is_alive()


def test_progress_monitor_failure():
    stdscr = None  # Use None for the curses window object
    update_interval = 0.1
    stop_event = threading.Event()

    # Create a list of sender threads with a failure rate of 100%
    senders = []
    for _ in range(3):
        message_queue = queue.Queue()
        sender = MessageSender(message_queue, failure_rate=1.0, mean_processing_time=0.1, stop_event=stop_event)
        senders.append(sender)

    progress_monitor = ProgressMonitor(stdscr, senders, update_interval, stop_event)
    progress_monitor.start()

    # Enqueue a message for each sender
    for sender in senders:
        sender.start()
        sender.message_queue.put(('1234567890', 'Test message'))

    # Wait for the senders to process the messages
    for sender in senders:
        sender.join()

    # Signal the stop event
    stop_event.set()

    # Wait for the progress monitor to stop
    progress_monitor.join()

    # Ensure the progress monitor stops gracefully
    assert not progress_monitor.is_alive()


def test_progress_monitor_graceful_stop():
    stdscr = None  # Use None for the curses window object
    update_interval = 0.1
    stop_event = threading.Event()

    # Create a list of sender threads
    senders = []
    for _ in range(3):
        message_queue = queue.Queue()
        sender = MessageSender(message_queue, failure_rate=0.0, mean_processing_time=0.1, stop_event=stop_event)
        senders.append(sender)

    progress_monitor = ProgressMonitor(stdscr, senders, update_interval, stop_event)
    progress_monitor.start()

    # Signal the stop event
    stop_event.set()

    # Wait for the progress monitor to stop
    progress_monitor.join()

    # Ensure the progress monitor stops gracefully
    assert not progress_monitor.is_alive()


def test_progress_monitor_sender_failure():
    stdscr = None  # Use None for the curses window object
    update_interval = 0.1
    stop_event = threading.Event()

    # Create a list of sender threads with a failure rate of 50%
    senders = []
    for _ in range(3):
        message_queue = queue.Queue()
        sender = MessageSender(message_queue, failure_rate=0.5, mean_processing_time=0.1, stop_event=stop_event)
        senders.append(sender)

    progress_monitor = ProgressMonitor(stdscr, senders, update_interval, stop_event)
    progress_monitor.start()

    # Enqueue a message for each sender
    for sender in senders:
        sender.start()
        sender.message_queue.put(('1234567890', 'Test message'))

    # Wait for the senders to process the messages
    for sender in senders:
        sender.join()

    # Signal the stop event
    stop_event.set()

    # Wait for the progress monitor to stop
    progress_monitor.join()

    # Ensure the progress monitor stops gracefully
    assert not progress_monitor.is_alive()


def test_progress_monitor_sender_exception():
    stdscr = None  # Use None for the curses window object
    update_interval = 0.1
    stop_event = threading.Event()

    # Create a list of sender threads with an exception during processing
    class ExceptionSender(MessageSender):
        def run(self):
            raise Exception("Simulated exception in sender")

    senders = [ExceptionSender(queue.Queue(), failure_rate=0.0, mean_processing_time=0.1, stop_event=stop_event) for _ in range(3)]

    progress_monitor = ProgressMonitor(stdscr, senders, update_interval, stop_event)
    progress_monitor.start()

    # Enqueue a message for each sender
    for sender in senders:
        sender.start()
        sender.message_queue.put(('1234567890', 'Test message'))

    # Wait for the senders to process the messages
    for sender in senders:
        sender.join()

    # Signal the stop event
    stop_event.set()

    # Wait for the progress monitor to stop
    progress_monitor.join()

    # Ensure the progress monitor stops gracefully
    assert not progress_monitor.is_alive()


def test_progress_monitor_successful_update(caplog):
    progress_queue = queue.Queue()
    update_interval = 1  # Set a short update interval for testing
    progress_monitor = ProgressMonitor(progress_queue, update_interval)

    # Start the progress monitor
    progress_monitor.start()

    # Send successful updates to the progress monitor
    for _ in range(5):
        progress_queue.put({'status': 'success', 'message': 'Task completed'})
        time.sleep(update_interval)

    # Stop the progress monitor
    progress_queue.put(None)
    progress_monitor.join()

    # Check log messages
    assert 'Task completed' in caplog.text
    assert 'ProgressMonitor completed.' in caplog.text

def test_progress_monitor_exception_handling(caplog):
    progress_queue = queue.Queue()
    update_interval = 1  # Set a short update interval for testing
    progress_monitor = ProgressMonitor(progress_queue, update_interval)

    # Start the progress monitor
    progress_monitor.start()

    # Send an exception update to the progress monitor
    progress_queue.put({'status': 'error', 'message': 'An error occurred'})

    # Stop the progress monitor
    progress_queue.put(None)
    progress_monitor.join()

    # Check log messages
    assert 'An error occurred' in caplog.text
    assert 'ProgressMonitor completed.' in caplog.text

def test_progress_monitor_no_updates(caplog):
    message_queue = queue.Queue()
    update_interval = 1  # Set a short update interval for testing
    stop_event = threading.Event()
    num_messages = 5
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    sender = MessageSender(message_queue, stop_event)
    progress_monitor = ProgressMonitor(None, message_queue, update_interval, stop_event)

    # Start the progress monitor
    progress_monitor.start()

    # Stop the progress monitor without sending any updates
    progress_queue.put(None)
    progress_monitor.join()

    # Check log messages
    assert 'ProgressMonitor completed.' in caplog.text

