from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.core.config import streams_collection
from app.core.dependencies import get_current_user, is_admin_by_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/DataStream")
async def data_stream_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse("data_stream.html", {"request": request, "active_page": "stream", "is_admin": is_admin_by_email(user_email)})


@router.get("/api/stream")
async def get_stream_data():
    docs = list(streams_collection.find({}, {"_id": 0}).sort("Timestamp", -1).limit(50))
    return {"data": docs}
