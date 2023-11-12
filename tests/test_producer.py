import queue
import threading
import time
from sms_alert_forge.producer import MessageProducer


def test_producer_no_messages():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 0
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.start()
    producer.join()

    assert message_queue.qsize() == num_senders
    assert all(message_queue.get() is None for _ in range(num_senders))
    assert not producer.is_alive()


def test_producer_some_messages():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 5
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.start()
    producer.join()

    assert message_queue.qsize() == num_messages + num_senders
    assert all(isinstance(message_queue.get(), tuple) for _ in range(num_senders))
    assert not producer.is_alive()


def test_producer_with_delay():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 5
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)

    # Start the producer, wait for some time, and then set the stop event
    producer.start()
    time.sleep(0.2)
    stop_event.set()
    producer.join()

    assert message_queue.qsize() == num_messages + num_senders
    assert all(isinstance(message_queue.get(), tuple) for _ in range(num_senders))
    assert not producer.is_alive()



def test_producer_interrupted():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 10
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.start()

    # Simulate an external interruption (e.g., user interrupt)
    time.sleep(1)
    stop_event.set()
    producer.join()

    # Ensure the producer stops gracefully
    assert not producer.is_alive()
    assert message_queue.qsize() > 0

