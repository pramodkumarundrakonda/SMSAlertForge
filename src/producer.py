import logging
import random
import threading
import time


class MessageProducer(threading.Thread):
    """
    Class responsible for simulating the generation of SMS messages and putting them into a queue.

    Attributes:
    - num_messages: Number of messages to generate.
    - message_queue: The queue to which the produced messages are added.
    - stop_event: Event to signal the thread to stop gracefully.
    - num_senders: Number of sender threads.
    """
    def __init__(self, num_messages, message_queue, stop_event, num_senders):
        super(MessageProducer, self).__init__()
        self.num_messages = num_messages
        self.message_queue = message_queue
        self.stop_event = stop_event
        self.num_senders = num_senders

    def run(self):
        try:
            logging.info("MessageProducer started.")

            for _ in range(self.num_messages):
                if self.stop_event.is_set():
                    break  # Check if the stop event is set, and stop if needed

                message = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=100))
                phone_number = random.randint(1000000000, 9999999999)
                self.message_queue.put((phone_number, message))
                time.sleep(0.1)
                logging.debug(f"Produced message: {message} for {phone_number}")

            logging.info("MessageProducer completed.")
            # Signal that no more messages will be produced
            for _ in range(self.num_senders):
                self.message_queue.put(None)

        except Exception as e:
            logging.error(f"Error in MessageProducer: {e}", exc_info=True)
