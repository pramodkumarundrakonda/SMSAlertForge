import threading
import queue
import time
from src.progressmonitor import ProgressMonitor
from src.sender import MessageSender


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
