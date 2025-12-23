import os
import time
import json
from kafka import KafkaConsumer, KafkaProducer

KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")
WARNING_THRESHOLD = int(os.environ.get("WARNING_THRESHOLD", 80))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL_THRESHOLD", 90))
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")


consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="vitals-monitor-group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


def monitor_vitals(vitals):
    value = vitals.get("value")
    if value is None:
        return

    if value > CRITICAL_THRESHOLD:
        alert_message = f"CRITICAL: Vitals value {value} exceeds critical threshold {CRITICAL_THRESHOLD}"
        producer.send(KAFKA_TOPIC, {"alert": alert_message, "severity": "critical"})
        producer.flush()
        print(alert_message)
    elif value > WARNING_THRESHOLD:
        alert_message = f"WARNING: Vitals value {value} exceeds warning threshold {WARNING_THRESHOLD}"
        producer.send(KAFKA_TOPIC, {"alert": alert_message, "severity": "warning"})
        producer.flush()
        print(alert_message)


if __name__ == "__main__":
    print("Starting vitals threshold monitor...")
    try:
        for message in consumer:
            vitals = message.value
            print(f"Received vitals: {vitals}")
            monitor_vitals(vitals)
    except KeyboardInterrupt:
        print("Stopping vitals threshold monitor.")
    finally:
        consumer.close()
        producer.close()