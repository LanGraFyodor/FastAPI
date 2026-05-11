import pytest
from fastapi import status

from src.models.sellers import Seller


@pytest.mark.asyncio()
async def test_create_token(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="seller@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.post(
        "/api/v1/token",
        json={"e_mail": "seller@example.com", "password": "secret"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


@pytest.mark.asyncio()
async def test_create_token_with_wrong_password(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail="seller@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.post(
        "/api/v1/token",
        json={"e_mail": "seller@example.com", "password": "wrong"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
