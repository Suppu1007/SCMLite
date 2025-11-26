# app/routes/home.py

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.core.config import users_collection, shipments_collection, streams_collection
from app.core.dependencies import get_current_user, is_admin_by_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -----------------------------------------------------------
# HOME PAGE (All users)
# -----------------------------------------------------------
@router.get("/home", response_class=HTMLResponse)
async def home(request: Request, user_email: str = Depends(get_current_user)):
    flash = request.cookies.get("flash")
    user = users_collection.find_one({"email": user_email})
    is_admin = is_admin_by_email(user_email)

    context = {
        "request": request,
        "user": user.get("name") if user else user_email,
        "shipment_count": shipments_collection.count_documents({}),
        "active_devices": streams_collection.count_documents({}),
        "active_page": "home",
        "is_admin": is_admin,
        "flash": flash
    }

    resp = templates.TemplateResponse("index.html", context)
    if flash:
        resp.delete_cookie("flash")
    return resp


# -----------------------------------------------------------
# DASHBOARD (Admin = full view, User = limited but same page)
# -----------------------------------------------------------
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_email: str = Depends(get_current_user)):
    flash = request.cookies.get("flash")
    user = users_collection.find_one({"email": user_email})
    is_admin = is_admin_by_email(user_email)

    # Common metrics
    total_shipments = shipments_collection.count_documents({})
    total_devices = streams_collection.count_documents({})
    deliveries_today = shipments_collection.count_documents({"status": "Delivered"})

    # Latest shipments for admin / user
    if is_admin:
        # Admin: see all recent shipments
        recent_shipments = list(
            shipments_collection.find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(5)
        )
        my_shipments = None
    else:
        # User: only their own shipments
        recent_shipments = []
        my_shipments = list(
            shipments_collection.find(
                {"$or": [
                    {"sender_email": user_email},
                    {"receiver_email": user_email},
                ]},
                {"_id": 0}
            ).sort("created_at", -1)
        )

    context = {
        "request": request,
        "active_page": "dashboard",
        "is_admin": is_admin,
        "user": user,
        "shipment_count": total_shipments,
        "active_devices": total_devices,
        "deliveries_today": deliveries_today,
        "recent_shipments": recent_shipments,
        "my_shipments": my_shipments,
        "flash": flash,
    }

    resp = templates.TemplateResponse("dashboard.html", context)
    if flash:
        resp.delete_cookie("flash")
    return resp
