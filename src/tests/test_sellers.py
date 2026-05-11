import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/seller"


async def create_seller(db_session, e_mail: str = "seller@example.com") -> Seller:
    seller = Seller(
        first_name="Ivan",
        last_name="Petrov",
        e_mail=e_mail,
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()

    return seller


async def get_token(async_client, seller: Seller) -> str:
    response = await async_client.post(
        "/api/v1/token",
        json={"e_mail": seller.e_mail, "password": "secret"},
    )

    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio()
async def test_create_seller(async_client):
    response = await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json={
            "first_name": "Ivan",
            "last_name": "Petrov",
            "e_mail": "seller@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": response.json()["id"],
        "first_name": "Ivan",
        "last_name": "Petrov",
        "e_mail": "seller@example.com",
    }
    assert "password" not in response.json()


@pytest.mark.asyncio()
async def test_get_all_sellers(db_session, async_client):
    seller = await create_seller(db_session)

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "sellers": [
            {
                "id": seller.id,
                "first_name": "Ivan",
                "last_name": "Petrov",
                "e_mail": "seller@example.com",
            }
        ]
    }
    assert "password" not in response.json()["sellers"][0]


@pytest.mark.asyncio()
async def test_get_single_seller_requires_token_and_returns_books(db_session, async_client):
    seller = await create_seller(db_session)
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.flush()
    token = await get_token(async_client, seller)

    unauthorized_response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")
    authorized_response = await async_client.get(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        headers=auth_header(token),
    )

    assert unauthorized_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert authorized_response.status_code == status.HTTP_200_OK
    assert authorized_response.json() == {
        "id": seller.id,
        "first_name": "Ivan",
        "last_name": "Petrov",
        "e_mail": "seller@example.com",
        "books": [
            {
                "id": book.id,
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2021,
                "pages": 104,
                "seller_id": seller.id,
            }
        ],
    }
    assert "password" not in authorized_response.json()


@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = await create_seller(db_session)

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json={
            "first_name": "Petr",
            "last_name": "Ivanov",
            "e_mail": "new@example.com",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": seller.id,
        "first_name": "Petr",
        "last_name": "Ivanov",
        "e_mail": "new@example.com",
    }
    assert "password" not in response.json()


@pytest.mark.asyncio()
async def test_delete_seller_deletes_books(db_session, async_client):
    seller = await create_seller(db_session)
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    sellers_result = await db_session.execute(select(Seller))
    books_result = await db_session.execute(select(Book))
    assert sellers_result.scalars().all() == []
    assert books_result.scalars().all() == []
