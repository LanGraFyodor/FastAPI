from pydantic import BaseModel

__all__ = [
    "TokenRequest",
    "TokenResponse",
]


class TokenRequest(BaseModel):
    e_mail: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
