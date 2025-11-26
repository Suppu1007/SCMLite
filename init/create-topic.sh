#!/bin/bash
set -e

echo "Waiting for Kafka to be ready..."

for i in {1..40}; do
  if /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list > /dev/null 2>&1; then
    echo "Kafka is ready!"
    break
  fi
  echo "Kafka not ready yet... retrying in 2s ($i/40)"
  sleep 2
done

# Create proper namespaced topic
TOPIC_NAME="device_data.streams"

echo "Creating topic: $TOPIC_NAME (if missing)..."
 /opt/kafka/bin/kafka-topics.sh --create \
  --topic "$TOPIC_NAME" \
  --bootstrap-server kafka:9092 \
  --partitions 1 \
  --replication-factor 1 \
  || echo "Topic '$TOPIC_NAME' already exists ✔"

echo "Kafka initialization complete ✔"
