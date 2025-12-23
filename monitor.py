import os
import time
import json
from kafka import KafkaConsumer, KafkaProducer
from collections import defaultdict

KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")
WARNING_THRESHOLD = int(os.environ.get("WARNING_THRESHOLD", 80))
CRITICAL_THRESHOLD = int(os.environ.get("CRITICAL_THRESHOLD", 90))
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
BREACH_WINDOW = int(os.environ.get("BREACH_WINDOW", 60))  # seconds
BREACH_COUNT_THRESHOLD = int(os.environ.get("BREACH_COUNT_THRESHOLD", 3))

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

# Track recent critical breaches per patient
patient_breaches = defaultdict(list)


def should_escalate(patient_id):
    now = time.time()
    # Remove old breaches
    patient_breaches[patient_id] = [
        ts for ts in patient_breaches[patient_id] if now - ts < BREACH_WINDOW
    ]

    # Check if escalation is needed
    if len(patient_breaches[patient_id]) >= BREACH_COUNT_THRESHOLD:
        return True
    else:
        return False


def monitor_vitals(vitals):
    patient_id = vitals.get("patient_id")
    value = vitals.get("value")

    if patient_id is None or value is None:
        print("Missing patient_id or value in vitals data.")
        return

    if value > CRITICAL_THRESHOLD:
        now = time.time()
        patient_breaches[patient_id].append(now)
        escalate = should_escalate(patient_id)

        alert_message = (
            f"CRITICAL: Vitals value {value} exceeds critical threshold {CRITICAL_THRESHOLD}"
        )
        if escalate:
            alert_message = f"ESCALATED: {alert_message}"
            escalation_metadata = {
                "breach_count": len(patient_breaches[patient_id]),
                "time_window": BREACH_WINDOW,
            }
        else:
            escalation_metadata = {}

        message = {
            "alert": alert_message,
            "severity": "critical",
            "escalation": escalation_metadata,
        }
        producer.send(KAFKA_TOPIC, message)
        producer.flush()
        print(alert_message)

    elif value > WARNING_THRESHOLD:
        alert_message = f"WARNING: Vitals value {value} exceeds warning threshold {WARNING_THRESHOLD}"
        message = {"alert": alert_message, "severity": "warning", "escalation": {}}
        producer.send(KAFKA_TOPIC, message)
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