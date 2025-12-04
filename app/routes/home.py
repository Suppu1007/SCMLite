# app/routes/home.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from app.core.config import users_collection, shipments_collection, streams_collection
from app.core.dependencies import get_current_user, is_admin_by_email
from app.main import templates



# UI
ui_router = APIRouter(tags=["Home"])

# API
api_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_user)])


@ui_router.get("/home", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request, user_email: str = Depends(get_current_user)):
    flash = request.cookies.get("flash")
    user = users_collection.find_one({"email": user_email})
    is_admin = is_admin_by_email(user_email)

    if is_admin:
        shipment_count = shipments_collection.count_documents({})
        active_devices = streams_collection.count_documents({})
    else:
        filter_query = {"$or": [
            {"sender_email": user_email},
            {"receiver_email": user_email},
        ]}
        shipment_count = shipments_collection.count_documents(filter_query)
        active_devices = shipment_count

    context = {
        "request": request,
        "user": user.get("name") if user else user_email,
        "shipment_count": shipment_count,
        "active_devices": active_devices,
        "active_page": "home",
        "is_admin": is_admin,
        "flash": flash,
    }

    resp = templates.TemplateResponse("index.html", context)
    if flash:
        resp.delete_cookie("flash")
    return resp


@ui_router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request, user_email: str = Depends(get_current_user)):
    flash = request.cookies.get("flash")
    user = users_collection.find_one({"email": user_email})
    is_admin = is_admin_by_email(user_email)

    if is_admin:
        shipment_count = shipments_collection.count_documents({})
        active_devices = streams_collection.count_documents({})
        deliveries_today = shipments_collection.count_documents({"status": "Delivered"})
        recent_shipments = list(
            shipments_collection.find({}, {"_id": 0}).sort("created_at", -1).limit(5)
        )
        my_shipments = None
    else:
        filter_query = {"$or": [
            {"sender_email": user_email},
            {"receiver_email": user_email},
        ]}
        my_shipments = list(
            shipments_collection.find(filter_query, {"_id": 0}).sort("last_updated", -1)
        )
        shipment_count = len(my_shipments)
        deliveries_today = len([s for s in my_shipments if s.get("status") == "Delivered"])
        active_devices = shipment_count
        recent_shipments = None

    context = {
        "request": request,
        "active_page": "dashboard",
        "is_admin": is_admin,
        "user": user.get("name") if user else user_email,
        "shipment_count": shipment_count,
        "active_devices": active_devices,
        "deliveries_today": deliveries_today,
        "recent_shipments": recent_shipments,
        "my_shipments": my_shipments,
        "flash": flash,
    }

    resp = templates.TemplateResponse("dashboard.html", context)
    if flash:
        resp.delete_cookie("flash")
    return resp


# ---------- API ----------

@api_router.get("/summary")
async def dashboard_summary(user_email: str = Depends(get_current_user)):
    is_admin = is_admin_by_email(user_email)

    if is_admin:
        shipment_count = shipments_collection.count_documents({})
        active_devices = streams_collection.count_documents({})
    else:
        shipment_count = shipments_collection.count_documents({
            "$or": [
                {"sender_email": user_email},
                {"receiver_email": user_email},
            ]
        })
        active_devices = shipment_count

    return {
        "user": user_email,
        "shipment_count": shipment_count,
        "active_devices": active_devices,
        "is_admin": is_admin,
    }
