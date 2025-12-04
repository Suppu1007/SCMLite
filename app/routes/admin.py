# app/routes/admin.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from datetime import datetime

from app.core.config import users_collection, role_history_collection
from app.core.dependencies import admin_required, get_current_user
from app.utils.email_utils import send_role_change_email
from app.main import templates


ui_router = APIRouter(tags=["Admin"], dependencies=[Depends(admin_required)])
api_router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(admin_required)])


# ---------- UI (HTML) ----------

@ui_router.get("/admin/users", include_in_schema=False)
async def admin_users_page(request: Request, user_email: str = Depends(get_current_user)):
    users = list(users_collection.find({}, {"password": 0}))
    flash = request.cookies.get("flash")

    response = templates.TemplateResponse("admin_users.html", {
        "request": request,
        "users": users,
        "active_page": "users",
        "is_admin": True,
        "flash": flash,
    })

    if flash:
        response.delete_cookie("flash")

    return response


# ----------- ROLE UPDATE (with email) -----------
@ui_router.post("/admin/users/update-role", include_in_schema=False)
async def update_user_role(
    request: Request,
    user_email_target: str = Form(...),
    new_role: str = Form(...),
    admin_email: str = Depends(get_current_user),
):

    user = users_collection.find_one({"email": user_email_target})
    if not user:
        response = RedirectResponse("/admin/users", status_code=303)
        response.set_cookie("flash", "User not found", max_age=4)
        return response

    old_role = user.get("role", "User")

    users_collection.update_one({"email": user_email_target}, {"$set": {"role": new_role}})

    # Record + Send Email ONLY IF role really changed
    if old_role != new_role:
        role_history_collection.insert_one({
            "target_user": user_email_target,
            "changed_by": admin_email,
            "old_role": old_role,
            "new_role": new_role,
            "timestamp": datetime.utcnow(),
        })

        try:
            send_role_change_email(
                to_email=user_email_target,
                username=user.get("name", user_email_target),
                old_role=old_role,
                new_role=new_role,
                changed_by=admin_email,
            )
        except Exception as e:
            print("Email Error:", e)

    response = RedirectResponse("/admin/users", status_code=303)
    response.set_cookie("flash", "Role updated successfully", max_age=4)
    return response

@ui_router.get("/admin/role-history", include_in_schema=False)
async def role_history_page(request: Request, admin_email: str = Depends(get_current_user)):
    history = list(role_history_collection.find({}, {"_id": 0}).sort("timestamp", -1))

    # Convert timestamp into readable text
    for item in history:
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S UTC")

    flash = request.cookies.get("flash")

    response = templates.TemplateResponse("role_history.html", {
        "request": request,
        "history": history,
        "active_page": "role_history",
        "is_admin": True,
        "flash": flash,
    })

    if flash:
        response.delete_cookie("flash")

    return response




# ----------- STATUS UPDATE -----------
@ui_router.post("/admin/users/update-status", include_in_schema=False)
async def update_user_status(
    request: Request,
    email: str = Form(...),
    status: str = Form(...),
    admin_email: str = Depends(get_current_user),
):

    user = users_collection.find_one({"email": email})
    if not user:
        response = RedirectResponse("/admin/users", status_code=303)
        response.set_cookie("flash", "User not found", max_age=4)
        return response

    users_collection.update_one({"email": email}, {"$set": {"status": status}})

    response = RedirectResponse("/admin/users", status_code=303)
    response.set_cookie("flash", "Status updated", max_age=4)
    return response


# ---------- API (Swagger) ----------

@api_router.get("/users")
async def api_list_users():
    return {"users": list(users_collection.find({}, {"password": 0}))}


@api_router.get("/role-history")
async def api_role_history():
    history = list(role_history_collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return {"history": history}
