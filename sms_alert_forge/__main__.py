"""
SMS Alert Simulation

This application simulates the process of sending SMS alerts. It includes a message producer, message senders, and a
progress monitor. The user can configure the simulation parameters through a YAML configuration file.

Modules:
- producer: Contains the MessageProducer class responsible for generating and placing messages into a queue.
- sender: Contains the MessageSender class responsible for sending messages from the queue to simulate SMS alerts.
- progressmonitor: Contains the ProgressMonitor class that monitors and displays the progress of the message sending
  process.

Usage:
Run the main script with a specified configuration file:

    python main.py --config <config_file.yaml>

"""

import curses
import queue
import sys
import threading
import logging
import yaml
import argparse
import os
import signal
import time
from datetime import datetime
from sms_alert_forge.producer import MessageProducer
from sms_alert_forge.sender import MessageSender
from sms_alert_forge.progressmonitor import ProgressMonitor

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'main_{time.strftime("%Y%m%d_%H%M%S")}.log')


def read_config(config_file):
    """
    Read configuration from a YAML file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        dict: Configuration parameters.
    """
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        # Check for empty fields in the configuration
        if not all(config.get(section) for section in ['logging', 'messages', 'senders', 'progress_monitor']):
            logging.error("One or more required fields are empty in the configuration. Exiting.")
            #sys.exit(1)

        return config
    except FileNotFoundError:
        logging.error(f"Config file '{config_file}' not found. Exiting.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Error reading YAML from '{config_file}': {e}. Exiting.")
        sys.exit(1)


def setup_logging(config):
    """
    Set up logging based on the configuration.

    Args:
        config (dict): Configuration parameters.
    """
    # Generate a log file name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_name = f"log_{timestamp}.log"

    # Use the 'logs' directory for the log file
    log_file_path = os.path.join(log_dir, log_file_name)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config['logging']['level']))

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')

    # Add console handler if configured
    if config['logging'].get('to_console', False):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if configured
    if config['logging'].get('to_file', False):
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def signal_handler(signum, frame):
    """
    Handle signals to stop the application gracefully.

    Args:
        signum (int): Signal number.
        frame (frame): Current stack frame.
    """
    logging.info(f"Received signal {signum}. Stopping gracefully.")
    os._exit(0)


def display_fancy_text(stdscr):
    """
    Display a fancy text at the center of the screen.

    Args:
        stdscr (curses.window): Curses window object.
    """
    try:
        # Function to display the fancy text at the center of the screen
        with open('banner.txt', 'r') as file:
            fancy_text = file.read()

        # Calculate the position to display the text at the center
        height, width = stdscr.getmaxyx()
        y = max(0, (height - fancy_text.count('\n')) // 2)
        x = max(0, (width - max(len(line) for line in fancy_text.split('\n'))) // 2)

        # Display the fancy text
        for line in fancy_text.split('\n'):
            stdscr.addstr(y, x, line)
            y += 1

        stdscr.refresh()

    except FileNotFoundError:
        logging.error("ASCII art file 'banner.txt' not found.")
    except Exception as e:
        logging.error(f"Error reading ASCII art file: {e}", exc_info=True)


def main(stdscr, config):
    """
    Main function to run the SMS alert simulation.

    Args:
        stdscr (curses.window): Curses window object.
        config (dict): Configuration parameters.
    """
    try:
        if stdscr:
            stdscr.clear()
            # Display fancy text
            display_fancy_text(stdscr)
            time.sleep(2)  # Sleep for 2 seconds to show the fancy text before starting the simulation

        logging.info("Main started.")

        stop_event = threading.Event()

        message_queue = queue.Queue()
        num_senders = config.get('senders', {}).get('num_senders')

        producer_config = {
            'num_messages': config['messages']['num_messages'],
            'message_queue': message_queue,
            'stop_event': stop_event,
            'num_senders': num_senders,
        }
        producer = MessageProducer(**producer_config)

        sender_config = {
            'message_queue': message_queue,
            'failure_rate': config['senders']['failure_rate'],
            'mean_processing_time': config['senders']['mean_processing_time'],
            'stop_event': stop_event,
        }
        senders = [MessageSender(**sender_config) for _ in range(config['senders']['num_senders'])]

        progress_monitor_config = {
            'stdscr': stdscr,
            'senders': senders,
            'update_interval': config['progress_monitor']['update_interval'],
            'stop_event': stop_event,
        }
        progress_monitor = ProgressMonitor(**progress_monitor_config)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        producer.start()
        for sender in senders:
            sender.start()
        progress_monitor.start()

        producer.join()
        for sender in senders:
            sender.join()

        progress_monitor.join()
        progress_monitor.stop()

        if stdscr:
            # Display a message and wait for user input before exiting
            stdscr.addstr(stdscr.getmaxyx()[0] - 1, 0, "Press 'q' to exit.")
            stdscr.refresh()

            while True:
                key = stdscr.getch()
                if key == ord('q'):
                    break

        logging.info("Main completed.")

    except Exception as e:
        logging.error(f"Error in main: {e}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate sending SMS alerts.')
    parser.add_argument('--config', default='config.yaml', help='Path to the configuration file in YAML format.')

    args = parser.parse_args()

    app_config = read_config(args.config)

    if not app_config:
        logging.error("Unable to read configurations. Exiting.")
    else:
        setup_logging(app_config)  # Set up logging based on the configuration
        curses.wrapper(main, app_config)
