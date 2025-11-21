from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from app.core.config import shipments_collection
from app.core.dependencies import get_current_user, is_admin_by_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/track_shipment")
async def track_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse(
        "track_shipment.html",
        {
            "request": request,
            "result": None,
            "error": None,
            "active_page": "track",
            "is_admin": is_admin_by_email(user_email)
        }
    )

@router.post("/track_shipment")
async def track_shipment(
    request: Request,
    shipment_id: str = Form(...),
    user_email: str = Depends(get_current_user)
):
    shipment = shipments_collection.find_one(
        {"shipment_id": shipment_id},
        {"_id": 0}
    )

    if not shipment:
        return templates.TemplateResponse(
            "track_shipment.html",
            {
                "request": request,
                "result": None,
                "error": "Shipment not found.",
                "active_page": "track",
                "is_admin": is_admin_by_email(user_email)
            }
        )

    return templates.TemplateResponse(
        "track_shipment.html",
        {
            "request": request,
            "result": shipment,
            "error": None,
            "active_page": "track",
            "is_admin": is_admin_by_email(user_email)
        }
    )
