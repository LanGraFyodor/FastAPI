from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import TokenRequest, TokenResponse
from src.services import authenticate_seller, create_access_token

auth_router = APIRouter(tags=["auth"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@auth_router.post("/token", response_model=TokenResponse)
async def create_token(credentials: TokenRequest, session: DBSession):
    seller = await authenticate_seller(
        session=session,
        e_mail=credentials.e_mail,
        password=credentials.password,
    )

    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(seller),
        "token_type": "bearer",
    }
