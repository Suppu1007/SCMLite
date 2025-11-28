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


# =======================================================
# LANDING PAGE (PUBLIC HOME)
# =======================================================
@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    token = request.cookies.get("access_token")

    # If user already logged in -> auto redirect
    if token:
        try:
            email = await get_current_user(request)
            if email:
                return RedirectResponse(
                    "/home" if is_admin_by_email(email) else "/dashboard",
                    status_code=303
                )
        except:
            pass

    flash = request.cookies.get("flash")
    response = templates.TemplateResponse(
        "landing.html",
        {"request": request, "flash": flash}
    )
    if flash:
        response.delete_cookie("flash")
    return response


# =======================================================
# LOGIN PAGE (GET)
# =======================================================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    flash = request.cookies.get("flash")
    response = templates.TemplateResponse(
        "login.html",
        {"request": request, "flash": flash}
    )
    if flash:
        response.delete_cookie("flash")
    return response


# =======================================================
# LOGIN ACTION (POST)
# =======================================================
@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    email_clean = email.strip()
    user = users_collection.find_one({"email": email_clean})

    if not user or not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "flash": "Invalid email or password",
                "entered_email": email_clean
            }
        )

    token = create_access_token(email_clean)

    destination = "/dashboard" if is_admin_by_email(email_clean) else "/home"

    resp = RedirectResponse(destination, status_code=303)
    resp.set_cookie("access_token", token, httponly=True, samesite="strict")
    resp.set_cookie("flash", "Login successful!", max_age=3, samesite="strict")
    return resp


# =======================================================
# SIGNUP PAGE (GET)
# =======================================================
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    flash = request.cookies.get("flash")
    response = templates.TemplateResponse(
        "signup.html",
        {"request": request, "flash": flash}
    )
    if flash:
        response.delete_cookie("flash")
    return response


# =======================================================
# SIGNUP ACTION (POST)
# =======================================================
@router.post("/signup")
async def signup_user(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    fullname = fullname.strip()
    email = email.strip()

    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "flash": "Passwords do not match!",
                "prefill_name": fullname,
                "prefill_email": email
            }
        )

    if users_collection.find_one({"email": email}):
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "flash": "User already exists!",
                "prefill_name": fullname,
                "prefill_email": email
            }
        )

    users_collection.insert_one({
        "name": fullname,
        "email": email,
        "password": hash_password(password),
        "role": "User",
        "status": "Active",
        "created_at": datetime.utcnow()
    })

    # Non-blocking email send
    try:
        send_account_created_email(email, fullname, password)
    except:
        pass

    resp = RedirectResponse("/login", status_code=303)
    resp.set_cookie("flash", "Signup successful! Please login.", max_age=4, samesite="strict")
    return resp


# =======================================================
# LOGOUT
# =======================================================
@router.get("/logout")
async def logout():
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("access_token")
    resp.set_cookie("flash", "Logged out successfully!", max_age=3, samesite="strict")
    return resp
