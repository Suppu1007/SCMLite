from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import os
import sys
import time

# ==============================
# CONFIG
# ==============================
<<<<<<< HEAD
=======

>>>>>>> dev
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = "device_streams"
MONGO_URL = os.getenv("MONGO_URL")

print(f"Using MONGO_URL = {MONGO_URL}")
print(f"Using KAFKA_BROKER = {KAFKA_BROKER}")

# ==============================
# MongoDB Connect
# ==============================
<<<<<<< HEAD
=======

>>>>>>> dev
def connect_mongo():
    try:
        client = MongoClient(
            MONGO_URL,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
        db = client["device_data"]
<<<<<<< HEAD
        print("✅ MongoDB connected")
        return db["streams"]
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
=======
        print("MongoDB connected")
        return db["streams"]
    except Exception as e:
        print("MongoDB connection failed:", e)
>>>>>>> dev
        sys.exit(1)

# ==============================
# Kafka Consumer
# ==============================
<<<<<<< HEAD
=======

>>>>>>> dev
def create_consumer():
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True
        )
<<<<<<< HEAD
        print("✅ Kafka consumer connected")
        return consumer
    except Exception as e:
        print("❌ Kafka connection failed:", e)
        sys.exit(1)

# ---------------------------------------------------------
# GLOBAL FIX — Create objects BEFORE consume loop
# ---------------------------------------------------------
collection = connect_mongo()      # <--- FIXED
consumer = create_consumer()      # <--- FIXED

print("🔥 Consumer is fully initialized\n")
=======
        print("Kafka consumer connected")
        return consumer
    except Exception as e:
        print("Kafka connection failed:", e)
        sys.exit(1)

collection = connect_mongo()      
consumer = create_consumer()     

print("Consumer is fully initialized\n")
>>>>>>> dev

# ==============================
# Consume Loop
# ==============================
<<<<<<< HEAD
=======

>>>>>>> dev
def consume_messages():
    while True:
        try:
            for msg in consumer:
                data = msg.value
<<<<<<< HEAD
                print("📩 Received:", data)

                try:
                    collection.insert_one(data)
                    print("💾 Saved to Mongo")
                except Exception as db_err:
                    print("❌ Mongo Insert Error:", db_err)

        except Exception as e:
            print("❌ Error in consumer loop:", e)
            time.sleep(3)

# ==============================
# Main
# ==============================
=======
                print(" Received:", data)

                try:
                    collection.insert_one(data)
                    print("Saved to Mongo")
                except Exception as db_err:
                    print(" Mongo Insert Error:", db_err)

        except Exception as e:
            print(" Error in consumer loop:", e)
            time.sleep(3)

# Main

>>>>>>> dev
if __name__ == "__main__":
    consume_messages()
