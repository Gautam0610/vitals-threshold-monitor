# vitals-threshold-monitor

Monitors vitals against configurable thresholds and emits alerts to Kafka.

## Usage

1.  **Set environment variables:**
    *   `KAFKA_TOPIC`: Kafka topic for vitals and alerts.
    *   `WARNING_THRESHOLD`: Warning threshold for vitals.
    *   `CRITICAL_THRESHOLD`: Critical threshold for vitals.
2.  **Run the Docker container:**
    ```bash
    docker run -e KAFKA_TOPIC=<your_kafka_topic> -e WARNING_THRESHOLD=<warning_value> -e CRITICAL_THRESHOLD=<critical_value> vitals-threshold-monitor
    ```