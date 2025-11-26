# app/routes/streams.py

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.core.config import streams_collection, shipments_collection
from app.core.dependencies import get_current_user, is_admin_by_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -----------------------------------------------------------
# IOT DATA STREAM PAGE (Admin + User)
# -----------------------------------------------------------
@router.get("/DataStream")
async def data_stream_page(request: Request, user_email: str = Depends(get_current_user)):
    is_admin = is_admin_by_email(user_email)

    return templates.TemplateResponse(
        "data_stream.html",
        {
            "request": request,
            "active_page": "stream",
            "is_admin": is_admin
        }
    )


# -----------------------------------------------------------
# IoT STREAM DATA API
# Admin = sees all
# User = sees only IoT data from their shipments
# -----------------------------------------------------------
@router.get("/api/stream")
async def get_stream_data(user_email: str = Depends(get_current_user)):
    is_admin = is_admin_by_email(user_email)

    if is_admin:
        docs = list(streams_collection.find({}, {"_id": 0}).sort("Timestamp", -1).limit(50))
    else:
        # Get all routes linked to the user in shipments
        user_shipments = shipments_collection.find(
            {"$or": [
                {"sender_email": user_email},
                {"receiver_email": user_email},
            ]}
        )

        allowed_routes = {(s["initial_location"], s["destination"]) for s in user_shipments}

        # Filter IoT stream using allowed route tuples
        docs = list(streams_collection.find(
            {"$or": [
                {
                    "Route_From": route[0],
                    "Route_To": route[1]
                } for route in allowed_routes
            ]},
            {"_id": 0}
        ).sort("Timestamp", -1).limit(50))

    return {"data": docs}
