from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.core.config import users_collection, role_history_collection
from app.core.dependencies import admin_required
from app.utils.email_utils import send_role_change_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -----------------------------------------------------------
# VIEW USER MANAGEMENT (Admins only)
# -----------------------------------------------------------

@router.get("/admin/users")
async def admin_users_page(
    request: Request,
    admin_email: str = Depends(admin_required)
):
    users = list(users_collection.find({}, {"password": 0}))
    flash = request.cookies.get("flash")

    resp = templates.TemplateResponse(
        "admin_users.html",
        {
            "request": request,
            "users": users,
            "active_page": "users",
            "is_admin": True,
            "flash": flash
        }
    )
    if flash:
        resp.delete_cookie("flash")
    return resp



# -----------------------------------------------------------
# ROLE UPDATE & ACCOUNT STATUS CHANGE (Admins only)
# -----------------------------------------------------------
@router.post("/admin/users")
async def admin_update_user(
    request: Request,
    user_email_target: str = Form(...),
    new_role: str = Form(...),
    action: str = Form(None),
    admin_email: str = Depends(admin_required),
):
    try:
        user = users_collection.find_one({"email": user_email_target})
        if not user:
            raise ValueError("User not found")

        old_role = user.get("role", "User")
        update_fields = {"role": new_role}

        # Status change blocker
        if action == "approve":
            update_fields["status"] = "Active"
        elif action == "disable":
            update_fields["status"] = "Disabled"

        # DB Update
        users_collection.update_one(
            {"email": user_email_target},
            {"$set": update_fields}
        )

        # Log Role Change
        role_history_collection.insert_one({
            "target_user": user_email_target,
            "changed_by": admin_email,
            "old_role": old_role,
            "new_role": new_role,
            "timestamp": datetime.utcnow()
        })

        # Email Notification (Safe)
        try:
            send_role_change_email(
                to_email=user_email_target,
                username=user.get("name", "User"),
                old_role=old_role,
                new_role=new_role,
                changed_by=admin_email
            )
        except Exception as e:
            print("⚠ Email failed:", e)

        # Success response
        response = RedirectResponse(url="/admin/users", status_code=303)
        response.set_cookie("flash", "User updated successfully!", max_age=4)
        return response

    except Exception as e:
        print("Admin Update Error:", e)
        response = RedirectResponse(url="/admin/users", status_code=303)
        response.set_cookie("flash", f"Update error: {e}", max_age=4)
        return response


# -----------------------------------------------------------
# ROLE HISTORY PAGE (Admins only)
# -----------------------------------------------------------
@router.get("/admin/role-history")
async def role_history_page(
    request: Request,
    admin_email: str = Depends(admin_required),
):
    flash = request.cookies.get("flash")

    # Fetch history sorted latest first
    history = list(
        role_history_collection.find({}, {"_id": 0}).sort("timestamp", -1)
    )

    # Convert datetime to readable string
    for item in history:
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S UTC")

    response = templates.TemplateResponse(
        "role_history.html",
        {
            "request": request,
            "active_page": "role_history",
            "is_admin": True,
            "flash": flash,
            "history": history
        }
    )

    if flash:
        response.delete_cookie("flash")

    return response

