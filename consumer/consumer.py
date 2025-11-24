# consumer/consumer.py
import os
import json
import time
from datetime import datetime
from kafka import KafkaConsumer
from pymongo import MongoClient


try:
    from app.utils.email_utils import notify_shipment_status_change
except Exception:
    notify_shipment_status_change = None

# CONFIG
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/")
DB_NAME = os.getenv("DB_NAME", "fastapi_auth_db")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "device_streams")  

# DB client
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
shipments_collection = db["shipments"]

def derive_status(data, shipment):
    """
    Rules:
      - If IoT Route_From equals shipment.destination -> Delivered
      - If battery < 3.0 -> Delayed (Low Battery)
      - If temperature > 35 -> Delayed (High Temp)
      - If shipment.status == 'Pending' -> 'In Transit'
      - otherwise -> 'In Transit'
    """
    try:
        battery = float(data.get("Battery_Level", 0) or 0)
    except Exception:
        battery = 0
    try:
        temp = float(data.get("Temperature", 0) or 0)
    except Exception:
        temp = 0

    route_from = (data.get("Route_From") or "").strip().lower()
    destination = (shipment.get("destination") or "").strip().lower()

    if route_from and destination and route_from == destination:
        return "Delivered"

    if battery and battery < 3.0:
        return "Delayed (Low Battery)"

    if temp and temp > 35:
        return "Delayed (High Temp)"

    if shipment.get("status") == "Pending":
        return "In Transit"

    return "In Transit"

def build_email_message(shipment, old_status, new_status, data):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    body = (
        f"Shipment Status Update\n\n"
        f"Shipment ID : {shipment['shipment_id']}\n"
        f"Old Status  : {old_status}\n"
        f"New Status  : {new_status}\n"
        f"Updated At  : {ts}\n\n"
        f"Current Location : {data.get('Route_From')}\n"
        f"Route            : {data.get('Route_From')} → {data.get('Route_To')}\n\n"
        f"IoT Sensor Data:\n"
        f"- Temperature : {data.get('Temperature')}\n"
        f"- Humidity    : {data.get('Humidity')}\n"
        f"- Battery     : {data.get('Battery_Level')}\n\n"
        f"Regards,\nSCMLite Auto-Tracking"
    )
    subject = f"SCMLite Update — {shipment['shipment_id']} is now {new_status}"
    return subject, body

def process_message(msg):
    try:
        raw = msg.value.decode("utf-8") if isinstance(msg.value, (bytes, bytearray)) else msg.value
        data = json.loads(raw)
    except Exception as e:
        print("Failed to parse message:", e)
        return

    route_to = (data.get("Route_To") or "").strip()
    if not route_to:
        print("Message missing Route_To, skipping.")
        return


   shipment = shipments_collection.find_one(
    {
        "$expr": {
            "$eq": [
                {"$trim": {"input": {"$toLower": "$destination"}}},
                route_to.strip().lower()
            ]
        },
        "status": {"$ne": "Delivered"}
    },
    sort=[("created_at", 1)]
    )


    if not shipment:
        print(f"No active shipment for destination '{route_to}'")
        return

    old_status = shipment.get("status", "Unknown")
    new_status = derive_status(data, shipment)

    update_fields = {
        "last_iot_data": data,
        "current_location": data.get("Route_From"),
        "last_updated": datetime.utcnow()
    }

    if new_status != old_status:
        shipments_collection.update_one(
            {"shipment_id": shipment["shipment_id"]},
            {
                "$set": {**update_fields, "status": new_status},
                "$push": {
                    "status_history": {
                        "from": old_status,
                        "to": new_status,
                        "ts": datetime.utcnow(),
                        "iot": data
                    }
                }
            }
        )

        subject, body = build_email_message(shipment, old_status, new_status, data)

        try:
            if notify_shipment_status_change:
                notify_shipment_status_change(shipment, old_status, new_status, data)
            else:
                try:
                    from app.utils.email_utils import _send_email
                    if shipment.get("sender_email"):
                        _send_email(shipment["sender_email"], subject, body)
                    if shipment.get("receiver_email"):
                        _send_email(shipment["receiver_email"], subject, body)
                except Exception:
                    print("Email helper not available; emails not sent.")
        except Exception as e:
            print("Email sending error:", e)

        print(f"Updated {shipment['shipment_id']}: {old_status} -> {new_status}")
    else:
        
        shipments_collection.update_one(
            {"shipment_id": shipment["shipment_id"]},
            {"$set": update_fields}
        )
        print(f"Refreshed IoT for {shipment['shipment_id']} (status unchanged).")

def main():
    retry = 0
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset="latest",
                enable_auto_commit=True,
                group_id="shipment-consumer-group"
            )
            print("Kafka consumer connected to:", KAFKA_BROKER)
            break
        except Exception as ex:
            retry += 1
            print("Kafka connect failed, retrying...", ex)
            time.sleep(min(5 * retry, 30))

    for msg in consumer:
        process_message(msg)

if __name__ == "__main__":
    main()
