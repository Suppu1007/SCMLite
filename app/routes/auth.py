# app/routes/auth.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.core.config import users_collection
from app.core.security import hash_password, verify_password
from app.utils.token_utils import create_access_token
from app.core.dependencies import get_current_user, is_admin_by_email
from app.utils.email_utils import send_account_created_email  

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# -------------------------------------------------------
# LOGIN PAGE (GET)
# -------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    token = request.cookies.get("access_token")

    # If already logged in, redirect to proper page
    if token:
        try:
            email = await get_current_user(request)
            if email:
                dest = "/dashboard" if is_admin_by_email(email) else "/home"
                return RedirectResponse(dest, status_code=303)
        except Exception:
            # invalid/expired token – just show login page
            pass

    flash = request.cookies.get("flash")
    response = templates.TemplateResponse(
        "login.html",
        {"request": request, "flash": flash}
    )
    if flash:
        response.delete_cookie("flash")
    return response


# -------------------------------------------------------
# LOGIN ACTION (POST)
# -------------------------------------------------------
@router.post("/", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = users_collection.find_one({"email": email.strip()})

    if not user or not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "flash": "Invalid email or password",
                "entered_email": email,
            }
        )

    token = create_access_token(email.strip())
    dest = "/dashboard" if is_admin_by_email(email.strip()) else "/home"

    resp = RedirectResponse(dest, status_code=303)
    resp.set_cookie("access_token", token, httponly=True, samesite="strict")
    resp.set_cookie("flash", "Login successful!", max_age=3)
    return resp


# -------------------------------------------------------
# SIGNUP PAGE (GET)
# -------------------------------------------------------
@router.get("/signup")
async def signup_page(request: Request):
    flash = request.cookies.get("flash")
    resp = templates.TemplateResponse(
        "signup.html",
        {"request": request, "flash": flash}
    )
    if flash:
        resp.delete_cookie("flash")
    return resp


# -------------------------------------------------------
# SIGNUP ACTION (POST)
# -------------------------------------------------------
@router.post("/signup")
async def signup_user(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    fullname_clean = fullname.strip()
    email_clean = email.strip()

    # 1) Password mismatch
    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "flash": "Passwords do not match",
                "prefill_name": fullname,
                "prefill_email": email,
            }
        )

    # 2) User already exists
    if users_collection.find_one({"email": email_clean}):
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "flash": "User already exists",
                "prefill_name": fullname,
                "prefill_email": email,
            }
        )

    # 3) Create user in DB
    users_collection.insert_one({
        "name": fullname_clean,
        "email": email_clean,
        "password": hash_password(password),
        "role": "User",
        "status": "Active",
        "created_at": datetime.utcnow()
    })

    # 4) Send welcome + credentials email (best-effort, non-blocking)
    try:
        send_account_created_email(
            to_email=email_clean,
            username=fullname_clean,
            password=password,
        )
    except Exception as e:
        print("Signup email error:", e)

    # 5) Redirect to login
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("flash", "Signup successful! Please login.", max_age=3)
    return resp


# -------------------------------------------------------
# LOGOUT
# -------------------------------------------------------
@router.get("/logout")
async def logout():
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("access_token")
    resp.set_cookie("flash", "Logged out successfully!", max_age=3)
    return resp
