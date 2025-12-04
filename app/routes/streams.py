# app/routes/streams.py

from fastapi import APIRouter, Request, Depends

from app.core.config import streams_collection, shipments_collection
from app.core.dependencies import get_current_user, is_admin_by_email
from app.main import templates



ui_router = APIRouter(tags=["Stream"])
api_router = APIRouter(prefix="/api/streams", tags=["Stream"], dependencies=[Depends(get_current_user)])


# ---------- UI (HTML) ----------

@ui_router.get("/DataStream", include_in_schema=False)
async def data_stream_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse(
        "data_stream.html",
        {
            "request": request,
            "active_page": "stream",
            "is_admin": is_admin_by_email(user_email),
        },
    )


# ---------- API (Swagger) ----------

@api_router.get("/")
async def get_stream_data(user_email: str = Depends(get_current_user)):
    is_admin = is_admin_by_email(user_email)

    if is_admin:
        docs = list(streams_collection.find({}, {"_id": 0}).sort("Timestamp", -1).limit(50))
    else:
        user_shipments = shipments_collection.find(
            {"$or": [
                {"sender_email": user_email},
                {"receiver_email": user_email},
            ]}
        )
        allowed_routes = {(s["initial_location"], s["destination"]) for s in user_shipments}

        docs = list(
            streams_collection.find(
                {"$or": [{"Route_From": r[0], "Route_To": r[1]} for r in allowed_routes]},
                {"_id": 0},
            )
            .sort("Timestamp", -1)
            .limit(50)
        )

    return {"data": docs}
