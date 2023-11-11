import threading
import queue
import time
from src.producer import MessageProducer


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

    assert message_queue.qsize() == num_senders
    assert all(isinstance(message_queue.get(), tuple) for _ in range(num_senders))
    assert not producer.is_alive()


def test_producer_stop_event():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 10
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)

    # Start the producer but set the stop event before it finishes
    producer.start()
    stop_event.set()
    producer.join()

    assert message_queue.qsize() == num_senders
    assert all(message_queue.get() is None for _ in range(num_senders))
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

    assert message_queue.qsize() == num_senders
    assert all(isinstance(message_queue.get(), tuple) for _ in range(num_senders))
    assert not producer.is_alive()


def test_producer_invalid_message_count():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = -1
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.start()
    producer.join()

    assert message_queue.qsize() == num_senders
    assert all(message_queue.get() is None for _ in range(num_senders))
    assert not producer.is_alive()


def test_producer_exception_during_generation():
    def generate_message_with_exception():
        raise ValueError("Error during message generation")

    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 5
    num_senders = 2

    # Override the message generation method to raise an exception
    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.generate_message = generate_message_with_exception

    producer.start()
    producer.join()

    assert message_queue.qsize() == num_senders
    assert all(message_queue.get() is None for _ in range(num_senders))
    assert not producer.is_alive()


def test_producer_exception_on_queue_put():
    def raise_exception_on_put(*args, **kwargs):
        raise ValueError("Error during queue.put()")

    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 5
    num_senders = 2

    # Override the queue.put method to raise an exception
    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.message_queue.put = raise_exception_on_put

    producer.start()
    producer.join()

    assert message_queue.qsize() == num_senders
    assert all(message_queue.get() is None for _ in range(num_senders))
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
    assert all(message_queue.get() is None for _ in range(message_queue.qsize()))


def test_producer_queue_full():
    message_queue = queue.Queue(maxsize=2)  # Set a small queue size
    stop_event = threading.Event()
    num_messages = 5
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.start()
    producer.join()

    # Ensure the producer stops, and the last messages indicate the queue is full
    assert not producer.is_alive()
    assert message_queue.qsize() == 2
    assert all(message_queue.get() is None for _ in range(2))


def test_producer_success_scenario():
    message_queue = queue.Queue()
    stop_event = threading.Event()
    num_messages = 10
    num_senders = 2

    producer = MessageProducer(num_messages, message_queue, stop_event, num_senders)
    producer.start()
    producer.join()

    # Ensure the producer stops, and all messages are successfully produced
    assert not producer.is_alive()
    assert message_queue.qsize() == num_senders
    assert all(isinstance(message_queue.get(), tuple) for _ in range(num_senders))
