import logging
import random
import threading
import time


class MessageSender(threading.Thread):
    """
    Class responsible for simulating the sending of SMS messages from a queue.

    Attributes:
    - message_queue: The queue from which messages are retrieved for sending.
    - failure_rate: The rate at which message sending can fail.
    - mean_processing_time: The mean time taken to process a message.
    - messages_sent: Number of messages successfully sent.
    - messages_failed: Number of messages that failed to be sent.
    - total_processing_time: Total time taken to process all messages.
    - stop_event: Event to signal the thread to stop gracefully.
    """

    def __init__(self, message_queue, failure_rate, mean_processing_time, stop_event):
        super(MessageSender, self).__init__()
        self.message_queue = message_queue
        self.failure_rate = failure_rate
        self.mean_processing_time = mean_processing_time
        self.messages_sent = 0
        self.messages_failed = 0
        self.total_processing_time = 0
        self.stop_event = stop_event

    def run(self):
        try:
            logging.info("MessageSender started.")

            while not self.stop_event.is_set():
                message = self.message_queue.get()

                if message is None:
                    break  # No more messages to send

                phone_number, _ = message

                processing_time = random.gauss(self.mean_processing_time, 0.1 * self.mean_processing_time)
                time.sleep(max(processing_time, 0))

                if random.random() < self.failure_rate:
                    self.messages_failed += 1
                    logging.warning("Message sending failed.")
                    logging.debug(f"Debug statement: Failed to send message to {phone_number}")
                else:
                    self.messages_sent += 1
                    self.total_processing_time += processing_time
                    logging.debug(f"Message sent successfully to {phone_number}. Processing time: {processing_time}")

            logging.info("MessageSender completed.")

        except Exception as e:
            logging.error(f"Error in MessageSender: {e}", exc_info=True)

