# Architecture Overview of vitals-threshold-monitor

## 1. Introduction

The `vitals-threshold-monitor` is a microservice designed to monitor incoming vitals data against predefined warning and critical thresholds. When a vital sign exceeds these thresholds, the system generates alerts and publishes them to a Kafka topic. The system also includes an escalation mechanism that triggers when a patient repeatedly breaches the critical threshold within a specified time window.

## 2. Data Flow

1.  **Vitals Data Ingestion:** The system consumes vitals data from a Kafka topic specified by the `KAFKA_TOPIC` environment variable. The vitals data is expected to be in JSON format and should include `patient_id` and `value` fields.
2.  **Threshold Evaluation:** The system evaluates the `value` field of each vital sign against the `WARNING_THRESHOLD` and `CRITICAL_THRESHOLD` environment variables.
3.  **Alert Generation:**
    *   If the `value` exceeds the `WARNING_THRESHOLD`, a warning alert is generated.
    *   If the `value` exceeds the `CRITICAL_THRESHOLD`, a critical alert is generated.
4.  **Escalation Logic:**
    *   The system tracks recent critical breaches for each patient using an in-memory dictionary (`patient_breaches`).
    *   The `should_escalate` function determines if an alert should be escalated based on the number of critical breaches within the `BREACH_WINDOW` and `BREACH_COUNT_THRESHOLD` environment variables.
5.  **Alert Publishing:** Alerts are published to the same Kafka topic (`KAFKA_TOPIC`) from which the vitals data is consumed. Alert messages are in JSON format and include the following fields:
    *   `alert`: A textual description of the alert.
    *   `severity`: The severity level of the alert (either "warning" or "critical").
    *   `escalation`: Metadata about the escalation, including `breach_count` and `time_window`, if the alert has been escalated.
6.  **Kafka Broker:** The system connects to a Kafka broker specified by the `KAFKA_BROKER` environment variable (defaulting to `localhost:9092`).

## 3. Configuration

The `vitals-threshold-monitor` is configured using environment variables:

*   `KAFKA_TOPIC`: The Kafka topic for consuming vitals data and publishing alerts.
*   `WARNING_THRESHOLD`: The threshold value above which a warning alert is generated (default: 80).
*   `CRITICAL_THRESHOLD`: The threshold value above which a critical alert is generated (default: 90).
*   `BREACH_WINDOW`: The time window (in seconds) within which multiple critical breaches are counted for escalation (default: 60).
*   `BREACH_COUNT_THRESHOLD`: The number of critical breaches within the `BREACH_WINDOW` required to trigger escalation (default: 3).
*   `KAFKA_BROKER`: The address of the Kafka broker (default: `localhost:9092`).

## 4. Escalation Logic

The escalation logic is implemented in the `should_escalate` function. This function maintains a dictionary (`patient_breaches`) that tracks the timestamps of recent critical breaches for each patient. When a critical breach occurs, the function checks if the number of breaches within the `BREACH_WINDOW` exceeds the `BREACH_COUNT_THRESHOLD`. If it does, the alert is escalated, and escalation metadata is included in the Kafka message.

## 5. Dependencies

*   Python 3.9
*   `kafka-python` library

## 6. Docker Deployment

The system is packaged as a Docker container. The `Dockerfile` specifies the base image, installs dependencies, copies the application code, and defines the command to start the application.

## 7. Future Enhancements

*   Implement a more sophisticated escalation policy (e.g., different escalation levels based on the number of breaches).
*   Add metrics and monitoring capabilities.
*   Implement a persistent storage mechanism for tracking patient breaches instead of relying on in-memory storage.
*   Add unit tests to improve code quality and reliability.