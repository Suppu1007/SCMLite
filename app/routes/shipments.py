# app/routes/shipments.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.core.config import shipments_collection
from app.core.dependencies import get_current_user, is_admin_by_email
from app.utils.email_utils import notify_shipment_status_change   

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -----------------------------------------------------------
# LOAD SHIPMENT CREATION PAGE
# -----------------------------------------------------------
@router.get("/create-shipment")
async def shipment_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse(
        "create_shipment.html",
        {
            "request": request,
            "active_page": "create",
            "is_admin": is_admin_by_email(user_email)
        }
    )


# -----------------------------------------------------------
# CREATE SHIPMENT
# -----------------------------------------------------------
@router.post("/create-shipment")
async def create_shipment(
    request: Request,
    shipment_id: str = Form(...),
    sender_name: str = Form(...),
    receiver_name: str = Form(...),
    sender_email: str = Form(...),
    receiver_email: str = Form(...),
    destination: str = Form(...),
    weight: float = Form(...),
    status: str = Form(...),
    user_email: str = Depends(get_current_user)
):
    # Duplicate ID Check
    if shipments_collection.find_one({"shipment_id": shipment_id}):
        return templates.TemplateResponse(
            "create_shipment.html",
            {
                "request": request,
                "flash": "Shipment ID already exists",
                "active_page": "create",
                "is_admin": is_admin_by_email(user_email)
            }
        )

    now = datetime.utcnow()

    # Create document
    shipment_doc = {
        "shipment_id": shipment_id,
        "sender_name": sender_name,
        "receiver_name": receiver_name,
        "sender_email": sender_email,
        "receiver_email": receiver_email,
        "destination": destination,
        "weight": weight,
        "status": status,
        "created_at": now,
        "last_updated": now,
        "status_history": [
            {"from": None, "to": status, "ts": now}
        ]
    }

    # Insert into DB
    shipments_collection.insert_one(shipment_doc)

    # ---------------------------------------------------
    # EMAIL NOTIFICATION USING NEW FUNCTION
    # ---------------------------------------------------
    try:
        notify_shipment_status_change(
            shipment=shipment_doc,
            old_status="Created",
            new_status=status,
            iot_data=None
        )
    except Exception as e:
        print("Email sending error:", e)

    # Redirect with flash message
    response = RedirectResponse("/create-shipment", status_code=303)
    response.set_cookie("flash", "Shipment created successfully", max_age=3)
    return response
