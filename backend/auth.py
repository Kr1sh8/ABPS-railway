"""
Authentication utilities — JWT tokens + standard hashlib SHA-256 with salt.
Works seamlessly across all Python versions without passlib/bcrypt incompatibility bugs.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import secrets
from jose import JWTError, jwt

SECRET_KEY = "abps-railway-secret-key-2024-secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def get_password_hash(password: str) -> str:
    """Hash password using salt + SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against salt$hash string."""
    try:
        salt, expected_hash = hashed_password.split("$")
        calc_hash = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
        return secrets.compare_digest(calc_hash, expected_hash)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
