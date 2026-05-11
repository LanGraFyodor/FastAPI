__all__ = [
    "authenticate_seller",
    "create_access_token",
    "get_current_seller",
]


import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.configurations.settings import settings
from src.models.sellers import Seller
from src.services.sellers import SellerService

JWT_EXPIRE_SECONDS = settings.jwt_expire_seconds
JWT_SECRET_KEY = settings.jwt_secret_key


def _encode_base64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decode_base64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(seller: Seller) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(seller.id),
        "e_mail": seller.e_mail,
        "exp": int(time.time()) + JWT_EXPIRE_SECONDS,
    }
    header_part = _encode_base64(json.dumps(header, separators=(",", ":")).encode())
    payload_part = _encode_base64(json.dumps(payload, separators=(",", ":")).encode())
    message = f"{header_part}.{payload_part}".encode()
    signature = hmac.new(
        JWT_SECRET_KEY.encode(),
        message,
        hashlib.sha256,
    ).digest()

    return f"{header_part}.{payload_part}.{_encode_base64(signature)}"


def _decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_part, payload_part, signature_part = token.split(".")
        message = f"{header_part}.{payload_part}".encode()
        expected_signature = hmac.new(
            JWT_SECRET_KEY.encode(),
            message,
            hashlib.sha256,
        ).digest()
        actual_signature = _decode_base64(signature_part)
    except (ValueError, binascii.Error):
        raise _credentials_exception()

    if not hmac.compare_digest(actual_signature, expected_signature):
        raise _credentials_exception()

    try:
        payload = json.loads(_decode_base64(payload_part))
        token_expires_at = int(payload.get("exp", 0))
    except (json.JSONDecodeError, binascii.Error, TypeError, ValueError):
        raise _credentials_exception()

    if token_expires_at < int(time.time()):
        raise _credentials_exception()

    return payload


async def authenticate_seller(
    session: AsyncSession,
    e_mail: str,
    password: str,
) -> Seller | None:
    seller = await SellerService(session).get_seller_by_email(e_mail)
    if seller is None:
        return None

    if not hmac.compare_digest(seller.password, password):
        return None

    return seller


async def get_current_seller(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> Seller:
    if authorization is None or not authorization.startswith("Bearer "):
        raise _credentials_exception()

    token = authorization.removeprefix("Bearer ").strip()
    payload = _decode_access_token(token)

    try:
        seller_id = int(payload.get("sub", 0))
    except (TypeError, ValueError):
        raise _credentials_exception()

    seller = await session.get(Seller, seller_id)
    if seller is None:
        raise _credentials_exception()

    return seller
