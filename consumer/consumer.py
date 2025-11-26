from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import os
import sys
import time

# ==========================================================
# CONFIGURATION
# ==========================================================

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = "device_streams"
MONGO_URL = os.getenv("MONGO_URL")

print(f"Using MONGO_URL = {MONGO_URL}")
print(f"Using KAFKA_BROKER = {KAFKA_BROKER}")
print(f"Listening to Topic = {TOPIC_NAME}")


# ==========================================================
# MONGODB CONNECTION
# ==========================================================

def connect_mongo():
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client["device_data"]
        print("MongoDB connected successfully.")
        return db["streams"]
    except Exception as e:
        print("MongoDB connection failed:", e)
        sys.exit(1)


# ==========================================================
# KAFKA CONSUMER SETUP
# ==========================================================

def create_consumer():
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="device_streams_consumer_grp"
        )
        print("Kafka consumer connected successfully.")
        return consumer
    except Exception as e:
        print("Kafka connection failed:", e)
        sys.exit(1)


collection = connect_mongo()
consumer = create_consumer()

print("\n Consumer is fully initialized and running...\n")


# ==========================================================
# KAFKA CONSUMPTION LOOP
# ==========================================================

def consume_messages():
    while True:
        try:
            for msg in consumer:
                data = msg.value
                print(f" Received → {data}")

                try:
                    collection.insert_one(data)
                    print("Saved to MongoDB")
                except Exception as db_error:
                    print(" MongoDB Insert Error:", db_error)

        except Exception as e:
            print(" Consumer Loop Error:", e)
            time.sleep(3)


# ==========================================================
# MAIN ENTRY
# ==========================================================

if __name__ == "__main__":
    consume_messages()
