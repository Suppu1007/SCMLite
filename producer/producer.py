from kafka import KafkaProducer
import socket
import json
import os
import sys
import time

# ==============================
# Configuration
# ==============================
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = "device_streams"
SOCKET_HOST = os.getenv("SOCKET_HOST", "socket_server")
SOCKET_PORT = int(os.getenv("SOCKET_PORT", 9999))

# ==============================
# Initialize Kafka Producer
# ==============================
def connect_kafka():
    """Create a Kafka producer instance."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print(f"Connected to Kafka broker at {KAFKA_BROKER}")
        return producer
    except Exception as e:
        print(f"Failed to connect to Kafka broker: {e}")
        sys.exit(1)

producer = connect_kafka()

# ==============================
# Connect to Socket Server
# ==============================
def connect_socket():
    """Connect to the FastAPI socket server."""
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SOCKET_HOST, SOCKET_PORT))
            print(f"Connected to socket at {SOCKET_HOST}:{SOCKET_PORT}")
            return client
        except ConnectionRefusedError:
            print(f"Socket server not ready... retrying in 3s")
            time.sleep(3)
        except socket.gaierror as e:
            print(f"Invalid socket address: {e}")
            time.sleep(5)

client = connect_socket()

# ==============================
# Main Loop
# ==============================
print("Kafka Producer running... waiting for data from socket.")

try:
    while True:
        data = client.recv(1024)
        if not data:
            continue

        try:
            msg = json.loads(data.decode("utf-8"))
            producer.send(TOPIC_NAME, msg)
            producer.flush()
            print(f"Sent to Kafka → {msg}")
        except json.JSONDecodeError:
            print(f"Skipped invalid JSON: {data}")

except KeyboardInterrupt:
    print("\nStopping producer...")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.close()
    producer.close()
    print("Producer stopped cleanly.")
