import bcrypt
import re
import requests
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    RECAPTCHA_SECRET_KEY
)

# =============================
# PASSWORD HASHING
# =============================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# =============================
# PASSWORD POLICY
# =============================
def validate_password(password: str) -> bool:
    """
    Rules:
    - Min length: 7
    - First char uppercase
    - At least 1 symbol
    """
    return (
        len(password) >= 7
        and password[0].isupper()
        and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )


# =============================
# JWT TOKENS (STRING SUBJECT)
# =============================
def create_access_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None



# =============================
# GOOGLE RECAPTCHA VERIFICATION
# =============================
def verify_recaptcha(recaptcha_response: str) -> bool:
    """
    Validates Google reCAPTCHA token server-side.
    Prevents bots bypassing client UI.
    """
    try:
        payload = {
            "secret": RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response,
        }
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload,
            timeout=5
        )
        result = response.json()
        return result.get("success", False)
    except Exception:
        return False
