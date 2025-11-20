import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# -----------------------------------------------------------
# PASSWORD HASHING
# -----------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a user's password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Check user password against the stored hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False  # prevents crash if hashed value is corrupted


# -----------------------------------------------------------
# JWT TOKENS
# -----------------------------------------------------------
def create_access_token(subject: str) -> str:
    """Create a JWT access token"""
    payload = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Decode JWT and return user email (subject)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
    except Exception:
        return None
