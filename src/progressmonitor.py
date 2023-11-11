import logging
import threading
import time


class ProgressMonitor(threading.Thread):
    """
    Class responsible for displaying and logging progress information of message sending.

    Attributes:
    - stdscr: The curses standard screen object for displaying information.
    - senders: List of MessageSender instances being monitored.
    - update_interval: The time interval between updates.
    - should_terminate: Event to signal termination of the thread.
    """
    def __init__(self, stdscr, senders, update_interval, stop_event):
        super(ProgressMonitor, self).__init__()
        self.stdscr = stdscr
        self.senders = senders
        self.update_interval = update_interval
        self.should_terminate = stop_event

    def run(self):
        try:
            logging.info("ProgressMonitor started.")

            start_time = time.time()

            while not self.should_terminate.is_set():
                time.sleep(self.update_interval)
                elapsed_time = time.time() - start_time

                total_sent = sum(sender.messages_sent for sender in self.senders)
                total_failed = sum(sender.messages_failed for sender in self.senders)
                average_time_per_message = sum(sender.total_processing_time for sender in self.senders) / total_sent if total_sent > 0 else 0

                all_senders_completed = not any(sender.is_alive() for sender in self.senders)
                self.stdscr.clear()
                self.stdscr.addstr(0, 0, f"Elapsed Time: {elapsed_time:.2f}s")
                self.stdscr.addstr(1, 0, f"Messages Sent: {total_sent}")
                self.stdscr.addstr(2, 0, f"Messages Failed: {total_failed}")
                self.stdscr.addstr(3, 0, f"Average Time per Message: {average_time_per_message:.2f}s")
                self.stdscr.refresh()

                logging.debug(f"Progress update. Elapsed Time: {elapsed_time:.2f}s | Messages Sent: {total_sent} | Messages Failed: {total_failed} | Average Time per Message: {average_time_per_message:.2f}s")

                # Check if the termination event is set
                if self.should_terminate.is_set():
                    logging.info("Termination event is set.")
                    break

                # Check if all sender threads have completed processing
                if all_senders_completed:
                    self.stop()
                    logging.info("All sender threads have completed processing.")
                    break

            logging.info("ProgressMonitor completed.")

        except Exception as e:
            logging.error(f"Error in ProgressMonitor: {e}", exc_info=True)

    def stop(self):
        self.should_terminate.set()
