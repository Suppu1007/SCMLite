# app/routes/shipments.py

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime

from app.core.config import shipments_collection, users_collection
from app.core.dependencies import get_current_user, is_admin_by_email
from app.utils.email_utils import send_shipment_created_email
from app.main import templates



ui_router = APIRouter(tags=["Shipments"])
api_router = APIRouter(prefix="/api/shipments", tags=["Shipments"], dependencies=[Depends(get_current_user)])


# ---------- UI (HTML) ----------

@ui_router.get("/create-shipment", include_in_schema=False)
async def create_shipment_page(
    request: Request,
    user_email: str = Depends(get_current_user)
):
    user = users_collection.find_one({"email": user_email})
    flash_msg = request.cookies.get("flash")

    response = templates.TemplateResponse("create_shipment.html", {
        "request": request,
        "user_email": user_email,
        "user_name": user.get("name") if user else user_email,
        "is_admin": is_admin_by_email(user_email),
        "active_page": "create",
        "flash": flash_msg,
    })

    if flash_msg:
        response.delete_cookie("flash")

    return response


# ---------- CREATE SHIPMENT ----------
@ui_router.post("/create-shipment", include_in_schema=False)
async def create_shipment_ui(
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
        # Only admins can create shipments for other senders
        is_admin = is_admin_by_email(user_email)
        if not is_admin and sender_email.lower() != user_email.lower():
            resp = RedirectResponse("/create-shipment", status_code=303)
            resp.set_cookie("flash", "⚠ You can only create shipments where YOU are the sender", max_age=4)
            return resp

        # Unique shipping ID validation
        if shipments_collection.find_one({"shipment_id": shipment_id}):
            resp = RedirectResponse("/create-shipment", status_code=303)
            resp.set_cookie("flash", "⚠ Shipment ID already exists!", max_age=4)
            return resp

        now = datetime.utcnow()

        shipment_doc = {
            "shipment_id": shipment_id.upper(),
            "sender_name": sender_name.strip(),
            "receiver_name": receiver_name.strip(),
            "sender_email": sender_email.strip().lower(),
            "receiver_email": receiver_email.strip().lower(),
            "initial_location": initial_location.strip().title(),
            "current_location": initial_location.strip().title(),
            "destination": destination.strip().title(),
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

        # --- SEND EMAIL TO BOTH SENDER AND RECEIVER ---
        try:
            send_shipment_created_email(shipment_doc, user_email)
        except Exception as email_error:
            print("Email Sending Error:", email_error)

        resp = RedirectResponse("/create-shipment", status_code=303)
        resp.set_cookie("flash", "Shipment created successfully", max_age=4)
        return resp

    except Exception as e:
        print("Shipment Creation Failed:", e)
        resp = RedirectResponse("/create-shipment", status_code=303)
        resp.set_cookie("flash", "Internal server error", max_age=4)
        return resp


# ---------- API (Swagger) ----------

@api_router.get("/")
async def list_shipments(user_email: str = Depends(get_current_user)):
    is_admin = is_admin_by_email(user_email)

    if is_admin:
        docs = list(shipments_collection.find({}, {"_id": 0}))
    else:
        docs = list(
            shipments_collection.find(
                {
                    "$or": [
                        {"sender_email": user_email},
                        {"receiver_email": user_email},
                    ]
                },
                {"_id": 0},
            )
        )
    return {"shipments": docs}


@api_router.get("/{shipment_id}")
async def get_shipment(shipment_id: str, user_email: str = Depends(get_current_user)):
    shipment = shipments_collection.find_one({"shipment_id": shipment_id.upper()}, {"_id": 0})
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if not is_admin_by_email(user_email) and shipment["sender_email"] != user_email and shipment["receiver_email"] != user_email:
        raise HTTPException(status_code=403, detail="Access denied")

    return shipment
