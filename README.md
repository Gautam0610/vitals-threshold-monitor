# vitals-threshold-monitor

Monitors vitals against configurable thresholds and emits alerts to Kafka.

## Usage

1.  **Set environment variables:**
    *   `KAFKA_TOPIC`: Kafka topic for vitals and alerts.
    *   `WARNING_THRESHOLD`: Warning threshold for vitals.
    *   `CRITICAL_THRESHOLD`: Critical threshold for vitals.
    *   `BREACH_WINDOW`: (Optional) Time window in seconds to consider for escalation (default: 60).
    *   `BREACH_COUNT_THRESHOLD`: (Optional) Number of critical breaches within the time window to trigger escalation (default: 3).
2.  **Run the Docker container:**
    ```bash
    docker run -e KAFKA_TOPIC=<your_kafka_topic> -e WARNING_THRESHOLD=<warning_value> -e CRITICAL_THRESHOLD=<critical_value> -e BREACH_WINDOW=<breach_window> -e BREACH_COUNT_THRESHOLD=<breach_count_threshold> vitals-threshold-monitor
    ```