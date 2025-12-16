# app/core/config.py

import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

load_dotenv()


RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")





# APP SECURITY CONFIG
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# MONGODB 
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "fastapi_auth_db")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL missing in environment!")

client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)

auth_db = client[DB_NAME]
stream_db = client.get_database("device_data")

users_collection = auth_db["users"]
shipments_collection = auth_db["shipments"]
role_history_collection = auth_db["role_history"]

streams_collection = stream_db["streams"]
iot_readings_collection = stream_db["iot_readings"]

# KAFKA CONFIG
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "device_streams")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "shipment-consumer-group")

# ADMIN ACCOUNT CONFIG
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def ensure_default_admin():
    existing = users_collection.find_one({"role": "Admin"})
    if existing:
        print("Admin exists:", existing["email"])
        return

    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        print("Missing admin environment variables!")
        return

    hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()

    users_collection.insert_one({
        "name": "Main Admin",
        "email": ADMIN_EMAIL,
        "password": hashed,
        "role": "Admin",
        "status": "Active",
        "created_at": datetime.utcnow(),
    })

    print("admin created:", ADMIN_EMAIL)


def get_consumer_collections():
    return {
        "shipments": shipments_collection,
        "iot_readings": iot_readings_collection,
    }
