from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.core.config import users_collection, shipments_collection, streams_collection
from app.core.dependencies import get_current_user, is_admin_by_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request, user_email: str = Depends(get_current_user)):
    flash = request.cookies.get("flash")
    user = users_collection.find_one({"email": user_email})
    context = {
        "request": request,
        "user": user.get("name") if user else user_email,
        "shipment_count": shipments_collection.count_documents({}),
        "active_devices": streams_collection.count_documents({}),
        "active_page": "home",
        "is_admin": is_admin_by_email(user_email),
        "flash": flash
    }
    resp = templates.TemplateResponse("index.html", context)
    if flash:
        resp.delete_cookie("flash")
    return resp


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user_email: str = Depends(get_current_user)):
    user = users_collection.find_one({"email": user_email})
    recent_shipments = list(shipments_collection.find({}, {"_id": 0}).sort("created_at", -1).limit(5))
    flash = request.cookies.get("flash")
    context = {
        "request": request,
        "active_page": "dashboard",
        "is_admin": is_admin_by_email(user_email),
        "shipment_count": shipments_collection.count_documents({}),
        "active_devices": streams_collection.count_documents({}),
        "deliveries_today": shipments_collection.count_documents({"status": "Delivered"}),
        "recent_shipments": recent_shipments,
        "flash": flash
    }
    resp = templates.TemplateResponse("dashboard.html", context)
    if flash:
        resp.delete_cookie("flash")
    return resp
