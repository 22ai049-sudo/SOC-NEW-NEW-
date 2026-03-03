from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core import state

# Use PBKDF2 to avoid bcrypt backend/runtime incompatibilities in some Python 3.12 images.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def _is_pbkdf2_hash(value: str) -> bool:
    return value.startswith("$pbkdf2-sha256$")


def bootstrap_users() -> None:
    for username, user in state.users.items():
        current_hash = user.get("hashed_password", "")
        if (not current_hash) or (not _is_pbkdf2_hash(current_hash)):
            user["hashed_password"] = pwd_context.hash(f"{username}123")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def authenticate_user(username: str, password: str):
    user = state.users.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
