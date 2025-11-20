from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.config import users_collection
from app.core.security import hash_password
from app.core.dependencies import get_current_user, is_admin_by_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/profile")
async def profile_page(request: Request, user_email: str = Depends(get_current_user)):
    user = users_collection.find_one({"email": user_email}, {"password": 0})
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "active_page": "profile", "is_admin": is_admin_by_email(user_email)})


@router.post("/profile")
async def update_profile(request: Request, fullname: str = Form(...), new_password: str = Form(None), user_email: str = Depends(get_current_user)):
    patch = {"name": fullname}
    if new_password and new_password.strip():
        patch["password"] = hash_password(new_password)
    users_collection.update_one({"email": user_email}, {"$set": patch})
    response = RedirectResponse("/profile", status_code=303)
    response.set_cookie("flash", "Profile updated", max_age=3)
    return response
