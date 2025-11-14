from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.hash import bcrypt
from pymongo import MongoClient
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv
import uvicorn
import os

# =========================================
# --- CONFIG ---
# =========================================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("MONGO_URL missing in .env!")

client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)

# =========================================
# FIXED ➜ correct DB for live stream data
# =========================================
auth_db = client["fastapi_auth_db"]      # users & shipments
stream_db = client["device_data"]        # live sensor stream

users_collection = auth_db["users"]
shipments_collection = auth_db["shipments"]
streams_collection = stream_db["streams"]  # <-- FIXED HERE

app = FastAPI(title="SCMLite RoyalBlue Edition")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# =========================================
# --- HELPERS ---
# =========================================

def create_access_token(data: dict):
    """Generate JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=303, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=303, detail="Invalid or expired token")


def is_admin(email: str):
    user = users_collection.find_one({"email": email})
    return user and user.get("role") == "Admin"


# =========================================
# --- LOGIN ---
# =========================================

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):

    user = users_collection.find_one({"email": email})

    if not user or not bcrypt.verify(password, user["password"]):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "flash": "Invalid email or password"
        })

    token = create_access_token({"sub": email})

    response = RedirectResponse("/home", status_code=303)
    response.set_cookie("access_token", token, httponly=True, max_age=3600, samesite="Lax")
    return response


# =========================================
# --- SIGNUP ---
# =========================================

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse)
async def signup_user(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):

    if password != confirm_password:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "flash": "Passwords do not match"
        })

    if users_collection.find_one({"email": email}):
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "flash": "User already exists"
        })

    hashed_pw = bcrypt.hash(password)

    users_collection.insert_one({
        "name": fullname,
        "email": email,
        "password": hashed_pw,
        "role": "User",
        "created_at": datetime.utcnow()
    })

    return RedirectResponse("/", status_code=303)


# =========================================
# --- HOME ---
# =========================================

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, user_email: str = Depends(get_current_user)):

    user = users_collection.find_one({"email": user_email})
    shipment_count = shipments_collection.count_documents({})

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user.get("name"),
        "shipment_count": shipment_count,
        "active_page": "home",
        "is_admin": is_admin(user_email)
    })


# =========================================
# --- PROFILE ---
# =========================================

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user_email: str = Depends(get_current_user)):

    user = users_collection.find_one({"email": user_email})

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "active_page": "profile",
        "is_admin": is_admin(user_email)
    })


@app.post("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    user_email: str = Depends(get_current_user),
    fullname: str = Form(...),
    new_password: str = Form(None)
):

    update_data = {"name": fullname}

    if new_password and new_password.strip():
        update_data["password"] = bcrypt.hash(new_password)

    users_collection.update_one({"email": user_email}, {"$set": update_data})

    return RedirectResponse("/profile", status_code=303)
# =========================================
# --- DASHBOARD---
# =========================================


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user_email: str = Depends(get_current_user)):

    shipment_count = shipments_collection.count_documents({})

    active_devices = streams_collection.count_documents({})

    today = datetime.utcnow().strftime("%Y-%m-%d")
    deliveries_today = shipments_collection.count_documents({"status": "Delivered"})

    recent_shipments = list(
        shipments_collection.find({}, {"_id": 0}).sort("created_at", -1).limit(5)
    )

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "is_admin": is_admin(user_email),
        "shipment_count": shipment_count,
        "active_devices": active_devices,
        "deliveries_today": deliveries_today,
        "recent_shipments": recent_shipments
    })


# =========================================
# --- USER MANAGEMENT ---
# =========================================

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request, user_email: str = Depends(get_current_user)):

    if not is_admin(user_email):
        return RedirectResponse("/home", status_code=303)

    users = list(users_collection.find({}, {"password": 0}))

    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "users": users,
        "active_page": "users",
        "is_admin": True
    })


@app.post("/admin/users", response_class=HTMLResponse)
async def update_user_role(
    request: Request,
    user_email: str = Depends(get_current_user),
    user_email_target: str = Form(...),
    new_role: str = Form(...)
):

    if not is_admin(user_email):
        return RedirectResponse("/home", status_code=303)

    users_collection.update_one(
        {"email": user_email_target},
        {"$set": {"role": new_role}}
    )

    return RedirectResponse("/admin/users", status_code=303)


# =========================================
# --- CREATE SHIPMENT ---
# =========================================

@app.get("/create-shipment", response_class=HTMLResponse)
async def shipment_page(request: Request, user_email: str = Depends(get_current_user)):

    return templates.TemplateResponse("create_shipment.html", {
        "request": request,
        "active_page": "create",
        "is_admin": is_admin(user_email)
    })


@app.post("/create-shipment", response_class=HTMLResponse)
async def create_shipment(
    request: Request,
    shipment_id: str = Form(...),
    sender_name: str = Form(...),
    receiver_name: str = Form(...),
    destination: str = Form(...),
    weight: float = Form(...),
    status: str = Form(...),
    user_email: str = Depends(get_current_user)
):

    if shipments_collection.find_one({"shipment_id": shipment_id}):
        return templates.TemplateResponse("create_shipment.html", {
            "request": request,
            "flash": "Shipment ID already exists",
            "active_page": "create",
            "is_admin": is_admin(user_email)
        })

    shipments_collection.insert_one({
        "shipment_id": shipment_id,
        "sender_name": sender_name,
        "receiver_name": receiver_name,
        "destination": destination,
        "weight": weight,
        "status": status,
        "created_at": datetime.utcnow()
    })

    return RedirectResponse("/create-shipment", status_code=303)


# =========================================
# --- LIVE DATA STREAM (FIXED) ---
# =========================================

@app.get("/DataStream", response_class=HTMLResponse)
async def data_stream_page(request: Request, user_email: str = Depends(get_current_user)):

    return templates.TemplateResponse("data_stream.html", {
        "request": request,
        "active_page": "stream",
        "is_admin": is_admin(user_email)
    })


@app.get("/api/stream")
async def get_stream_data():

    docs = list(
        streams_collection
        .find({}, {"_id": 0})
        .sort("Timestamp", -1)
        .limit(50)
    )

    return {"status": "success", "data": docs}


# =========================================
# --- LOGOUT ---
# =========================================

@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response


# =========================================
# --- RUN ---
# =========================================

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
