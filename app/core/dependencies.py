from fastapi import Request, HTTPException, status

from app.core.security import decode_token
from app.core.config import users_collection


async def get_current_user(request: Request) -> str:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=303, detail="Not authenticated")

    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=303, detail="Invalid or expired token")

    return email


def is_admin_by_email(email: str) -> bool:
    user = users_collection.find_one({"email": email})
    return bool(user and user.get("role") == "Admin")
