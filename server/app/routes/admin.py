from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.core.config import users_collection, role_history_collection
from app.core.dependencies import get_current_user, is_admin_by_email
from app.core.security import hash_password
from app.utils.email_utils import send_role_change_email

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -----------------------------------------------------------
# ADMIN: VIEW USERS
# -----------------------------------------------------------
@router.get("/admin/users")
async def admin_users(request: Request, user_email: str = Depends(get_current_user)):
    if not is_admin_by_email(user_email):
        return RedirectResponse("/home", status_code=303)

    users = list(users_collection.find({}, {"password": 0}))

    return templates.TemplateResponse(
        "admin_users.html",
        {
            "request": request,
            "users": users,
            "active_page": "users",
            "is_admin": True
        }
    )


# -----------------------------------------------------------
# ADMIN: CREATE NEW USER
# -----------------------------------------------------------
@router.post("/admin/users/create")
async def admin_create_user(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    role: str = Form("User"),
    user_email: str = Depends(get_current_user)
):
    if not is_admin_by_email(user_email):
        return RedirectResponse("/home", status_code=303)

    if users_collection.find_one({"email": email}):
        flash = "User already exists"
    else:
        users_collection.insert_one({
            "name": fullname,
            "email": email,
            "password": hash_password("ChangeMe123!"),
            "role": role,
            "status": "Active",
            "created_at": datetime.utcnow()
        })
        flash = f"User {email} created."

    users = list(users_collection.find({}, {"password": 0}))

    return templates.TemplateResponse(
        "admin_users.html",
        {
            "request": request,
            "users": users,
            "flash": flash,
            "active_page": "users",
            "is_admin": True
        }
    )


# -----------------------------------------------------------
# ADMIN: UPDATE ROLE / STATUS
# -----------------------------------------------------------
@router.post("/admin/users")
async def update_user_role(
        request: Request,
        user_email: str = Depends(get_current_user),
        user_email_target: str = Form(...),
        new_role: str = Form(...),
        action: str = Form(None)
):
    if not is_admin_by_email(user_email):
        return RedirectResponse("/home", status_code=303)

    target = users_collection.find_one({"email": user_email_target})

    if not target:
        flash = "User not found."
    else:
        old_role = target.get("role", "User")

        # Update role
        users_collection.update_one(
            {"email": user_email_target},
            {"$set": {"role": new_role}}
        )

        # Update status
        if action == "approve":
            users_collection.update_one({"email": user_email_target}, {"$set": {"status": "Active"}})
        elif action == "disable":
            users_collection.update_one({"email": user_email_target}, {"$set": {"status": "Disabled"}})

        # Log the change
        role_history_collection.insert_one({
            "target_user": user_email_target,
            "changed_by": user_email,
            "old_role": old_role,
            "new_role": new_role,
            "timestamp": datetime.utcnow()
        })

        # ✔ FIXED EMAIL FUNCTION CALL (now passing 4 args)
        send_role_change_email(
            to_email=user_email_target,
            new_role=new_role,
            old_role=old_role,
            changed_by=user_email
        )

        flash = f"{user_email_target}'s role updated."

    users = list(users_collection.find({}, {"password": 0}))
    return templates.TemplateResponse(
        "admin_users.html",
        {"request": request, "users": users, "flash": flash, "active_page": "users", "is_admin": True}
    )

# -----------------------------------------------------------
# ADMIN: ROLE HISTORY
# -----------------------------------------------------------
@router.get("/admin/role-history")
async def role_history(request: Request, user_email: str = Depends(get_current_user)):
    if not is_admin_by_email(user_email):
        return RedirectResponse("/home", status_code=303)

    history = list(
        role_history_collection.find({}, {"_id": 0}).sort("timestamp", -1)
    )

    return templates.TemplateResponse(
        "role_history.html",
        {
            "request": request,
            "history": history,
            "active_page": "role_history",
            "is_admin": True
        }
    )
