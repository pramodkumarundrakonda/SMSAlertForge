import threading
import queue
import time
from sms_alert_forge.sender import MessageSender


def test_sender_success():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue actual messages
    message_queue.put(('1234567890', 'Test message 1'))
    message_queue.put(('9876543210', 'Test message 2'))

    # Enqueue None to signal sender threads to stop
    message_queue.put(None)

    # Wait for the sender to process the message
    sender.join()

    # Ensure the sender stops and the message is successfully sent
    assert not sender.is_alive()
    assert sender.messages_sent == 2
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
    # Enqueue None to signal sender threads to stop
    message_queue.put(None)

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

    message_queue.put(None)
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
    for _ in range(1000):
        message_queue.put(('1234567890', 'Test message'))
    message_queue.put(None)
    # Simulate an external interruption (e.g., user interrupt)
    time.sleep(1)
    stop_event.set()
    sender.join()

    # Ensure the sender stops gracefully
    assert not sender.is_alive()


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
    message_queue.put(None)
    # Wait for the sender to process the message
    sender.join()

    # Ensure the sender stops and the custom exception is caught
    assert not sender.is_alive()


def test_sender_graceful_stop():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    failure_rate = 0.0
    mean_processing_time = 0.1

    sender = MessageSender(message_queue, failure_rate, mean_processing_time, stop_event)
    sender.start()

    # Enqueue a message for sending
    message_queue.put(('1234567890', 'Test message'))
    message_queue.put(None)
    # Signal the stop event
    stop_event.set()

    # Wait for the sender to stop
    sender.join()

    # Ensure the sender stops gracefully, and the message is not sent
    assert not sender.is_alive()
