import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# ---------------------------
# Environment Variables
# ---------------------------
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "fastapi_auth_db")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL missing in .env")

# ---------------------------
# MongoDB Client
# ---------------------------
client = MongoClient(
    MONGO_URL,
    tls=True,
    tlsAllowInvalidCertificates=True
)

# ---------------------------
# Databases
# ---------------------------
auth_db = client[DB_NAME]
stream_db = client.get_database("device_data")

# ---------------------------
# Collections
# ---------------------------
users_collection = auth_db["users"]
shipments_collection = auth_db["shipments"]
streams_collection = stream_db["streams"]
role_history_collection = auth_db["role_history"]
