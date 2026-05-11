from pydantic import BaseModel, ConfigDict

from .books import ReturnedBook

__all__ = [
    "IncomingSeller",
    "ReturnedAllSellers",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "UpdateSeller",
]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


class IncomingSeller(BaseSeller):
    password: str


class UpdateSeller(BaseSeller):
    pass


class ReturnedSeller(BaseSeller):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ReturnedSellerWithBooks(ReturnedSeller):
    model_config = ConfigDict(from_attributes=True)

    books: list[ReturnedBook]


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
