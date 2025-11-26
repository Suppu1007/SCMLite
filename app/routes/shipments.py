from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.core.config import shipments_collection, users_collection
from app.core.dependencies import get_current_user, is_admin_by_email
from app.utils.email_utils import send_shipment_created_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -------------------------------
# Create Shipment Page (Admin + Users)
# -------------------------------
@router.get("/create-shipment")
async def create_shipment_page(request: Request, user_email: str = Depends(get_current_user)):
    
    user = users_collection.find_one({"email": user_email})
    flash_msg = request.cookies.get("flash")

    response = templates.TemplateResponse(
        "create_shipment.html",
        {
            "request": request,
            "user_email": user_email,
            "user_name": user.get("name"),
            "is_admin": is_admin_by_email(user_email),
            "active_page": "create",
            "flash": flash_msg,
        }
    )

    if flash_msg:
        response.delete_cookie("flash")

    return response


# -------------------------------
# Create Shipment (POST)
# -------------------------------

@router.post("/create-shipment")
async def create_shipment(
    request: Request,
    shipment_id: str = Form(...),
    sender_name: str = Form(...),
    receiver_name: str = Form(...),
    sender_email: str = Form(...),
    receiver_email: str = Form(...),
    initial_location: str = Form(...),
    destination: str = Form(...),
    weight: float = Form(...),
    status: str = Form(...),
    user_email: str = Depends(get_current_user),
):
    try:
        is_admin = is_admin_by_email(user_email)

        if not is_admin and sender_email.lower() != user_email.lower():
            response = RedirectResponse("/create-shipment", status_code=303)
            response.set_cookie("flash", "You can only create shipments where YOU are the sender!", max_age=4)
            return response

        if shipments_collection.find_one({"shipment_id": shipment_id}):
            response = RedirectResponse("/create-shipment", status_code=303)
            response.set_cookie("flash", "Shipment ID already exists!", max_age=4)
            return response

        now = datetime.utcnow()
        shipment_doc = {
            "shipment_id": shipment_id,
            "sender_name": sender_name.strip(),
            "receiver_name": receiver_name.strip(),
            "sender_email": sender_email.strip(),
            "receiver_email": receiver_email.strip(),
            "initial_location": initial_location.strip(),
            "current_location": initial_location.strip(),
            "destination": destination.strip().lower(),
            "weight": float(weight),
            "status": status,
            "created_at": now,
            "last_updated": now,
            "last_iot_data": None,
            "status_history": [{
                "from": None,
                "to": status,
                "ts": now,
                "iot": None,
            }],
            "created_by": user_email,
        }

        shipments_collection.insert_one(shipment_doc)

        try:
            send_shipment_created_email(shipment_doc)
        except Exception as email_error:
            print("Email Error:", email_error)

        response = RedirectResponse("/create-shipment", status_code=303)
        response.set_cookie("flash", "Shipment created successfully!", max_age=4)
        return response

    except Exception as e:
        print("🚨 Shipment Create Error:", e)
        response = RedirectResponse("/create-shipment", status_code=303)
        response.set_cookie("flash", "Internal Server Error — check logs!", max_age=4)
        return response
