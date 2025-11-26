# app/routes/tracking.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates

from app.core.dependencies import get_current_user, is_admin_by_email
from app.services.shipments_service import (
    get_shipment_by_id,
    format_shipment_for_view,
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------------------------
# TRACK PAGE UI (Admin + User)
# ------------------------------------------------------------------
@router.get("/track_shipment")
async def track_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse(
        "track_shipment.html",
        {
            "request": request,
            "result": None,
            "error": None,
            "last_iot": None,
            "history": None,
            "active_page": "track",
            "is_admin": is_admin_by_email(user_email),
        },
    )


# ------------------------------------------------------------------
# TRACK SHIPMENT SEARCH (Admin + User Restricted)
# ------------------------------------------------------------------
@router.post("/track_shipment")
async def track_shipment(
    request: Request,
    shipment_id: str = Form(...),
    user_email: str = Depends(get_current_user),
):
    shipment_doc = get_shipment_by_id(shipment_id.strip())

    # Shipment not found
    if not shipment_doc:
        return templates.TemplateResponse(
            "track_shipment.html",
            {
                "request": request,
                "result": None,
                "error": "Shipment not found.",
                "last_iot": None,
                "history": None,
                "active_page": "track",
                "is_admin": is_admin_by_email(user_email),
            },
        )

    # Restrict access for non-admin users
    is_admin = is_admin_by_email(user_email)
    if not is_admin:
        # Only sender or receiver can track
        if shipment_doc.get("sender_email") != user_email and shipment_doc.get("receiver_email") != user_email:
            return templates.TemplateResponse(
                "track_shipment.html",
                {
                    "request": request,
                    "result": None,
                    "error": " You do not have access to this shipment.",
                    "last_iot": None,
                    "history": None,
                    "active_page": "track",
                    "is_admin": False,
                },
            )

    # Format shipment for UI
    shipment, history = format_shipment_for_view(shipment_doc)

    return templates.TemplateResponse(
        "track_shipment.html",
        {
            "request": request,
            "result": shipment,
            "last_iot": shipment.get("last_iot_data"),
            "history": history,
            "error": None,
            "active_page": "track",
            "is_admin": is_admin,
        },
    )
