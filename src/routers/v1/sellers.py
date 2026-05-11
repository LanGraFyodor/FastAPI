from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import (
    IncomingSeller,
    ReturnedAllSellers,
    ReturnedSeller,
    ReturnedSellerWithBooks,
    UpdateSeller,
)
from src.services import SellerService, get_current_seller

sellers_router = APIRouter(tags=["seller"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]
CurrentSeller = Annotated[Seller, Depends(get_current_seller)]


@sellers_router.post("/seller", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
@sellers_router.post("/seller/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_seller(seller: IncomingSeller, session: DBSession):
    new_seller = await SellerService(session).add_seller(seller)

    if new_seller is None:
        return Response(status_code=status.HTTP_409_CONFLICT)

    return new_seller


@sellers_router.get("/seller", response_model=ReturnedAllSellers)
@sellers_router.get("/seller/", response_model=ReturnedAllSellers, include_in_schema=False)
async def get_all_sellers(session: DBSession):
    sellers = await SellerService(session).get_all_sellers()
    return {"sellers": sellers}


@sellers_router.get("/seller/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_single_seller(seller_id: int, session: DBSession, _: CurrentSeller):
    seller = await SellerService(session).get_single_seller(seller_id)

    if seller is not None:
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@sellers_router.put("/seller/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: UpdateSeller, session: DBSession):
    seller = await SellerService(session).update_seller(seller_id, seller_data)

    if seller is not None:
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@sellers_router.delete("/seller/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await SellerService(session).delete_seller(seller_id)

    if not deleted_seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
