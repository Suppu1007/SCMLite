from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.core.config import shipments_collection
from app.core.dependencies import get_current_user, is_admin_by_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/create-shipment")
async def shipment_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse("create_shipment.html", {"request": request, "active_page": "create", "is_admin": is_admin_by_email(user_email)})


@router.post("/create-shipment")
async def create_shipment(request: Request,
                          shipment_id: str = Form(...),
                          sender_name: str = Form(...),
                          receiver_name: str = Form(...),
                          destination: str = Form(...),
                          weight: float = Form(...),
                          status: str = Form(...),
                          user_email: str = Depends(get_current_user)):
    if shipments_collection.find_one({"shipment_id": shipment_id}):
        return templates.TemplateResponse("create_shipment.html", {"request": request, "flash": "Shipment ID already exists", "active_page": "create", "is_admin": is_admin_by_email(user_email)})
    shipments_collection.insert_one({
        "shipment_id": shipment_id,
        "sender_name": sender_name,
        "receiver_name": receiver_name,
        "destination": destination,
        "weight": weight,
        "status": status,
        "created_at": datetime.utcnow()
    })
    response = RedirectResponse("/create-shipment", status_code=303)
    response.set_cookie("flash", "Shipment created", max_age=3)
    return response
