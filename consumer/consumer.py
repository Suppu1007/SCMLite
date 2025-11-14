from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import os
import sys
import time

# ==============================
# Configuration
# ==============================
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = "device_streams"
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# ==============================
# MongoDB Connection
# ==============================
def connect_mongo():
    """Connect to MongoDB (local or Atlas)."""
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client["device_data"]
        print(" MongoDB connected successfully.")
        return db["streams"]
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        sys.exit(1)

collection = connect_mongo()

# ==============================
# Kafka Consumer Setup
# ==============================
def create_consumer():
    """Create a Kafka Consumer instance."""
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=10000
        )
        print(f"Listening for messages on topic: {TOPIC_NAME}")
        return consumer
    except Exception as e:
        print(f"Failed to connect to Kafka broker: {e}")
        sys.exit(1)

consumer = create_consumer()

# ==============================
# Consume and Store Messages
# ==============================
def consume_messages():
    """Continuously consume messages from Kafka and store in MongoDB."""
    while True:
        try:
            for message in consumer:
                data = message.value
                if not data:
                    continue
                print(f"Received: {data}")
                collection.insert_one(data)
                print("Stored in MongoDB")
        except Exception as e:
            print(f"Error processing message: {e}")
            time.sleep(3)  # wait before retrying

# ==============================
# Entry Point
# ==============================
if __name__ == "__main__":
    print("Starting Kafka Consumer...")
    try:
        consume_messages()
    except KeyboardInterrupt:
        print("\nConsumer stopped manually.")
    finally:
        consumer.close()
        print("Kafka Consumer connection closed.")
