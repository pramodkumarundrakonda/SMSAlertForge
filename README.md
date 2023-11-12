# SMSAlertForge

### Overview

`SMSAlertForge` is a Python-based simulation tool designed to emulate SMS alerting scenarios. It is particularly useful for testing and validating systems that depend on SMS notifications. The application comprises different modules that work together to simulate message generation, sending, and monitoring.

### Features

- **Message Generation**: The application can simulate the generation of a specified number of messages with random content and phone numbers.

- **Message Sending**: Messages are simulated to be sent through multiple sender threads, each capable of simulating successful or failed message delivery.

- **Progress Monitoring**: A dedicated progress monitor provides real-time updates on the number of messages sent, failed, and average processing time.

- **Configurability**: The behavior of the application is highly customizable through a configuration file (`config.yaml`), allowing users to adjust parameters such as logging levels, the number of messages, and sender behavior.

### How to Use

1. **Configuration**: Edit the `config.yaml` file to configure the simulation according to your needs. Adjust parameters such as logging levels, the number of messages, sender behavior, and update intervals.

2. **Running the Simulation**: Execute the simulation using the following command:

   ```bash
   make run
   ```

3. **Testing**: Ensure the reliability of the simulation by running tests:

   ```bash
   make test
   ```

# SMSAlertForge Console Output

Here is a simulation of SMSAlertForge in action, demonstrating the console output during a typical run. The console output provides valuable insights into the progress of message generation, sending, and overall system performance.

![Console Output](output.gif)

*Note: This GIF is a visual representation of the console output and provides a quick overview of the system's behavior.*



# Exploring Features

## Configuration

SMSAlertForge offers extensive configuration options through a YAML file. This file defines parameters that influence the simulation. Below is an in-depth explanation of each section in the configuration file (`config.yaml`):

```yaml
logging:
    level: INFO
    to_console: true
    to_file: false

messages:
    num_messages: 100

senders:
    num_senders: 5
    failure_rate: 0.1
    mean_processing_time: 0.2

progress_monitor:
    update_interval: 0.5
```

### Logging

- **level:** The logging level (e.g., INFO, DEBUG).
- **to_console:** Whether to log messages to the console.
- **to_file:** Whether to log messages to a file.

### Messages

- **num_messages:** The total number of messages to be generated in the simulation.

### Senders

- **num_senders:** The number of sender threads in the simulation.
- **failure_rate:** The probability of a sender thread failing to send a message.
- **mean_processing_time:** The average time it takes for a sender to process a message.

### Progress Monitor

- **update_interval:** The time interval between progress updates.


### Libraries Used for Configuration

SMSAlertForge relies on the following Python libraries to achieve its functionality:

### [YAML (PyYAML)](https://pyyaml.org/)

PyYAML is a YAML parser and emitter for Python. It is used in SMSAlertForge to handle the configuration file (`config.yaml`). With PyYAML, users can easily define and modify simulation parameters in a human-readable format.

To install PyYAML, run the following command:

```bash
pip install pyyaml
```

Ensure that you have PyYAML installed before running SMSAlertForge to parse and process the configuration file seamlessly.

Note: Don't worry about manual library installations; the Makefile automates the process for you. Just use the Makefile commands mentioned below for a hassle-free setup.
Now, let's delve into the capabilities of the Makefile.

---

## Using the Makefile

SMSAlertForge provides a convenient Makefile that streamlines common tasks for users. The Makefile includes the following targets:

### Install Requirements

To install the necessary dependencies, run the following command:

```bash
make install_requirements
```

This ensures that all required libraries are installed based on the contents of the `requirements.txt` file.

### Run SMSAlertForge

Executing SMSAlertForge is as simple as running:

```bash
make run
```

This command sets up the Python environment and launches the application with default configurations. Users don't need to worry about lengthy Python commands; the Makefile takes care of it.

### Run Tests

Ensure the integrity of SMSAlertForge by running the test suite:

```bash
make test
```

This command executes the tests in the `tests` directory, ensuring that the application functions as expected.

### Clean Up

To remove temporary files and caches, use:

```bash
make clean
```

This command helps keep your project directory tidy.

### All-in-One

For a streamlined experience, you can use the following command to install requirements, run the application, and execute tests:

```bash
make all
```

This command is particularly useful if you want to perform all necessary tasks in one go. Thanks to the `.PHONY` targets, it ensures that the listed tasks are always executed.

**Note:** Make sure to adjust the configurations in `conf/config.yaml` for custom settings.


---

## Delving into Individual Components

Now, let's explore the inner workings of the SMSAlertForge application by examining its individual components. Each module contributes distinct functionalities, working in tandem to simulate the end-to-end process of sending SMS alerts.



## `producer.py` 

### Message Generation

The `producer.py` module is tasked with generating random messages to be processed by the sender threads. The key features include:

#### Random Message Generation

Messages are created with a length of 100 characters, consisting of a mix of alphanumeric characters.

#### Enqueuing Messages

The generated messages are enqueued into a shared message queue, ensuring a synchronized flow of messages for subsequent processing by sender threads.

### Threading

To facilitate concurrent processing, the `producer.py` module operates as a dedicated thread. This allows for efficient message generation while maintaining the overall integrity of the simulation.

### Logging

Detailed logs are maintained for each message, providing insights into the success or failure of the message generation process.

### Usage

To explore the implementation details, refer to the source code in [`producer.py`](./sms_alert_forge/producer.py).

This module's functionality is integral to simulating the message generation process within the SMSAlertForge application.

---



### `sender.py`

The `sender.py` module is responsible for simulating the behavior of a message sender. It emulates the process of sending messages to specified phone numbers, incorporating features such as failure rates and processing times to simulate real-world scenarios.

#### Key Features:

1. **Failure Simulation:**
   - The sender introduces a configurable failure rate, allowing you to mimic scenarios where message delivery fails.

2. **Processing Time:**
   - The module simulates varying processing times, providing insights into how different message processing durations can impact the overall system.

3. **Logging:**
   - Detailed logs are generated to track the success and failure of message sending operations. These logs play a crucial role in understanding the application's behavior.

#### Implementation Details:

- The module operates in a separate thread, allowing concurrent execution alongside other components of the application.

- It utilizes Python's `random` module to introduce randomness in failure rates and processing times, creating a realistic simulation environment.

- Logging is employed to capture essential information about each message-sending event, aiding in monitoring and debugging.

By exploring the `sender.py` module, users gain valuable insights into how message sending is simulated, providing a comprehensive understanding of SMSAlertForge's functionality.

Stay tuned as we move on to the next module, exploring the intricacies of SMSAlertForge step by step!

---


### `progressmonitor.py`

The `progressmonitor.py` module orchestrates the visual and log-based representation of the progress of message sending within the SMSAlertForge application. It employs the `curses` library to create a simple and effective console-based user interface for monitoring real-time progress.

#### Key Features:

1. **Visual Progress Display:**
   - Utilizes the `curses` library to create a dynamic, console-based display that visually represents the progress of message sending.

2. **Real-Time Updates:**
   - Regularly updates the display to reflect the latest statistics, including elapsed time, the number of messages sent, messages failed, and the average time per message.

3. **Termination Handling:**
   - Monitors a termination event, ensuring a graceful exit when the application completes its operation or upon user intervention.

#### Implementation Details:

- **Curses Library:**
  - The `curses` library provides a terminal-independent way to handle text-based user interfaces in a console environment.

- **Dynamic Display:**
  - The display is updated at regular intervals, offering real-time insights into the progress of message sending operations.

- **Integration with Other Components:**
  - Collaborates with the `MessageSender` instances to fetch the latest statistics for display, creating a synchronized and coherent monitoring experience.

- **Termination Handling:**
  - Monitors a termination event, ensuring the application can gracefully stop and exit upon completion or user interruption.

Understanding the `progressmonitor.py` module sheds light on how SMSAlertForge seamlessly combines visual representation with backend processing, providing users with an informative and interactive experience.

---


### `__main__.py`

The `__main__.py` module serves as the entry point for the SMSAlertForge application, orchestrating the setup, configuration, and coordination of various components.

#### Key Features:

1. **Configuration Handling:**
   - Reads and interprets the application configuration from a YAML file using the PyYAML library.

2. **Logging Infrastructure:**
   - Establishes a comprehensive logging infrastructure to capture essential information, warnings, errors, and debugging details.

3. **Signal Handling:**
   - Implements signal handling to gracefully respond to user interruptions, ensuring a controlled shutdown of the application.

4. **Multithreading for Parallel Processing:**
   - Utilizes multithreading to concurrently execute the `MessageProducer`, `MessageSender`, and `ProgressMonitor` components.

5. **Dynamic Progress Monitoring:**
   - Integrates the `ProgressMonitor` to provide users with a real-time visual representation of the progress of message sending.

## Implementation Details:


### Signal Handling in `__main__.py`

#### Purpose:

Signal handling in SMSAlertForge serves the crucial purpose of responding gracefully to external signals, specifically the `SIGINT` signal. This ensures that the application can be terminated by users without causing unexpected disruptions.

#### Implementation:

1. **Setting Up Signal Handling:**
   - The `setup_signal_handler` function initializes the signal handling mechanism by associating the `signal_handler` function with the `SIGINT` signal.
   - It uses the `signal` module to set up the handler: `signal.signal(signal.SIGINT, signal_handler)`.

2. **Signal Handler Function:**
   - The `signal_handler` function is triggered when a `SIGINT` signal is received.
   - It logs a message indicating the reception of the signal and sets the `stop_event` to signal termination.

3. **Integration with Threads:**
   - SMSAlertForge relies on multiple threads, such as `MessageProducer`, `MessageSender`, and `ProgressMonitor`, running concurrently.
   - The `stop_event` is a shared event that acts as a communication channel among threads. When set, it signals threads to conclude their tasks and exit gracefully.

4. **Termination Protocol:**
   - Threads regularly check the status of the `stop_event`. If set, they initiate the termination protocol, allowing ongoing processes to complete before exiting.
   - This ensures that the application gracefully handles interruptions, avoiding abrupt terminations that might result in data corruption or incomplete operations.

#### Benefits:

- **Graceful Termination:**
  - Signal handling ensures that ongoing processes are given the opportunity to complete before the application exits, preventing data loss or corruption.

- **Thread Coordination:**
  - The shared `stop_event` is integral for effective communication between threads, enabling them to synchronize their termination and avoid race conditions.

- **User-Friendly Interruption:**
  - Users can interrupt the application by sending a `SIGINT` signal, providing a convenient and standard way to stop the program.

---

### Logging in `__main__.py`

#### Purpose:

Logging is a crucial aspect of SMSAlertForge, providing a mechanism to record informational messages, warnings, and errors. Proper logging ensures transparency, aids in debugging, and provides insights into the application's runtime behavior.

#### Implementation:

1. **Logging Configuration:**
   - The `setup_logging` function configures the logging system based on the provided configuration settings.
   - It sets the logging level, specifies output destinations (console and/or file), and defines the log format.

2. **Log Messages:**
   - Throughout the code, various log messages are strategically placed to convey important events, such as the start and completion of the main process, signal reception, and progress updates.

3. **Logging Levels:**
   - Different log levels (e.g., INFO, WARNING, DEBUG) are utilized to categorize messages based on their significance. For instance, INFO messages provide high-level information, while DEBUG messages offer detailed insights for debugging.

---

### Usage of Threads in `__main__.py`

#### Purpose:

SMSAlertForge employs a multi-threaded architecture to efficiently handle different aspects of the application concurrently. Threads are utilized to manage message production, sending, and progress monitoring independently.

#### Implementation:

1. **Thread Creation:**
   - Threads are created for `MessageProducer`, `MessageSender`, and `ProgressMonitor` instances, each responsible for a specific aspect of the application.

2. **Thread Coordination:**
   - The `stop_event` is a shared event among threads, acting as a signal to terminate operations gracefully.
   - Threads regularly check the status of the `stop_event` to determine whether they should conclude their tasks.

3. **Termination Protocol:**
   - When the `stop_event` is set (usually in response to a `SIGINT` signal), threads initiate a termination protocol, allowing them to complete ongoing processes before exiting.

#### Benefits:

- **Concurrent Processing:**
  - Multi-threading enables simultaneous execution of different components, improving overall efficiency and responsiveness.

- **Isolation of Tasks:**
  - Each thread is dedicated to a specific task, promoting code modularity and simplifying maintenance.

- **Graceful Termination:**
  - The shared `stop_event` ensures that all threads can gracefully terminate their operations, preventing data corruption or incomplete tasks.



By combining signal handling, logging, and multi-threading, SMSAlertForge achieves a robust and responsive design, capable of handling diverse tasks concurrently while providing informative feedback to users and developers.

---

### Conclusion

SMSAlertForge is a versatile and robust SMS simulation tool designed to provide a seamless and insightful experience for users. Leveraging a combination of signal handling, logging, and multi-threading, the application ensures efficient message production, sending, and progress monitoring. Here's a brief overview of what SMSAlertForge has to offer:

1. **Ease of Use:**
   - The `Makefile` simplifies the execution process, handling dependencies and providing a one-command solution for running the application.

2. **Configuration Management:**
   - SMSAlertForge utilizes the PyYAML library to parse and process configuration files, allowing users to customize various parameters seamlessly.

3. **Signal Handling:**
   - Graceful termination is facilitated through signal handling, enabling users to interrupt the application without compromising ongoing processes.

4. **Logging System:**
   - The logging system offers transparency and diagnostic insights, recording important events and providing users with feedback about the application's progress.

5. **Multi-Threading Architecture:**
   - Threads are employed to concurrently manage message production, sending, and progress monitoring, enhancing efficiency and responsiveness.

6. **User-Friendly Execution:**
   - Users can run SMSAlertForge with minimal manual intervention, thanks to the provided `Makefile` that handles all necessary configurations and dependencies.

7. **Insightful Feedback:**
   - Log messages and progress updates keep users informed about the application's runtime behavior, making the experience user-friendly and informative.


Explore the detailed documentation above to understand how SMSAlertForge works and make the most out of its features.

---

