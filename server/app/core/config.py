import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

# -----------------------------------------------------------
# LOAD ENVIRONMENT
# -----------------------------------------------------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "fastapi_auth_db")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL missing in environment!")


# -----------------------------------------------------------
# MONGO CLIENT (one client only)
# -----------------------------------------------------------
client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)

auth_db = client[DB_NAME]
stream_db = client.get_database("device_data")

users_collection = auth_db["users"]
shipments_collection = auth_db["shipments"]
streams_collection = stream_db["streams"]
role_history_collection = auth_db["role_history"]


# -----------------------------------------------------------
# ENSURE DEFAULT ADMIN (called once on startup)
# -----------------------------------------------------------
def ensure_default_admin():
    existing = users_collection.find_one({"role": "Admin"})
    if existing:
        print("✔ Admin exists:", existing["email"])
        return

    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        print("⚠ ADMIN_EMAIL or ADMIN_PASSWORD missing, cannot create default admin.")
        return

    hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()

    users_collection.insert_one({
        "name": "Main Admin",
        "email": ADMIN_EMAIL,
        "password": hashed,
        "role": "Admin",
        "status": "Active",
        "created_at": datetime.utcnow()
    })

    print("✔ Default Admin Created:", ADMIN_EMAIL)
