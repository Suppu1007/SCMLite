# app/core/dependencies.py

from fastapi import Request, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.core.security import decode_token
from app.core.config import users_collection


def _extract_token(request: Request) -> str | None:
    """
    Priority:
    1. Cookie: access_token  (browser UI)
    2. Authorization: Bearer <token>  (Swagger / API clients)
    """
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[len("Bearer "):].strip()

    return None


def get_current_user(request: Request) -> str:
    token = _extract_token(request)

    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    email = decode_token(token)
    if not email:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return email


def is_admin_by_email(email: str) -> bool:
    user = users_collection.find_one({"email": email})
    return bool(user and user.get("role") == "Admin")


def user_required(user_email: str = Depends(get_current_user)):
    return user_email


def admin_required(user_email: str = Depends(get_current_user)):
    if not is_admin_by_email(user_email):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user_email
