import threading
import queue
import time
from src.sender import MessageSender


def test_sender_success():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))

    # Wait for the sender to process the message
    sender.join()

    # Ensure the sender stops and the message is successfully sent
    assert not sender.is_alive()
    assert sender.messages_sent == 1
    assert sender.messages_failed == 0


def test_sender_failure():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 1.0  # High failure rate for testing failure scenarios
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))

    # Wait for the sender to process the message
    sender.join()

    # Ensure the sender stops and the message fails to send
    assert not sender.is_alive()
    assert sender.messages_sent == 0
    assert sender.messages_failed == 1


def test_sender_multiple_messages():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue multiple messages for sending
    for _ in range(5):
        message_queue.put(('1234567890', 'Test message'))

    # Wait for the sender to process all messages
    sender.join()

    # Ensure the sender stops, and all messages are successfully sent
    assert not sender.is_alive()
    assert sender.messages_sent == 5
    assert sender.messages_failed == 0


def test_sender_interrupted():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))

    # Simulate an external interruption (e.g., user interrupt)
    time.sleep(1)
    stop_event.set()
    sender.join()

    # Ensure the sender stops gracefully
    assert not sender.is_alive()
    assert sender.messages_sent == 0
    assert sender.messages_failed == 0


def test_sender_unexpected_exception():
    class CustomException(Exception):
        pass

    def raise_custom_exception(*args, **kwargs):
        raise CustomException("This is a custom exception")

    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0
    mean_processing_time = 0.1

    # Override the run method to raise a custom exception
    MessageSender.run = raise_custom_exception

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))

    # Wait for the sender to process the message
    sender.join()

    # Ensure the sender stops and the custom exception is caught
    assert not sender.is_alive()
    assert sender.messages_sent == 0
    assert sender.messages_failed == 1

    # Restore the original run method
    MessageSender.run = MessageSender._original_run


def test_sender_negative_processing_time():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0

    # Use a negative mean_processing_time to test invalid input
    mean_processing_time = -0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))

    # Wait for the sender to process the message
    sender.join()

    # Ensure the sender stops gracefully, and the message is not sent
    assert not sender.is_alive()
    assert sender.messages_sent == 0
    assert sender.messages_failed == 0


def test_sender_invalid_failure_rate():
    message_queue = queue.Queue()
    stop_event = threading.Event()

    # Use an invalid failure_rate (greater than 1.0)
    failure_rate = 1.5
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))

    # Wait for the sender to process the message
    sender.join()

    # Ensure the sender stops gracefully, and the message is not sent
    assert not sender.is_alive()
    assert sender.messages_sent == 0
    assert sender.messages_failed == 0


def test_sender_graceful_stop():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))

    # Signal the stop event
    stop_event.set()

    # Wait for the sender to stop
    sender.join()

    # Ensure the sender stops gracefully, and the message is not sent
    assert not sender.is_alive()
    assert sender.messages_sent == 0
    assert sender.messages_failed == 0
