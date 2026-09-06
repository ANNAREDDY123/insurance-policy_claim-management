from datetime import date

from pydantic import BaseModel, Field


PAYMENT_METHODS = {
    "UPI",
    "Card",
    "Net Banking",
    "Auto Debit",
}

PAYMENT_STATUSES = {
    "Pending",
    "Success",
    "Failed",
}


class PaymentCreate(BaseModel):
    amount: float = Field(
        ...,
        gt=0,
    )

    payment_date: date

    payment_method: str

    transaction_id: str = Field(
        ...,
        min_length=3,
        max_length=150,
    )

    payment_status: str = "Pending"


class PaymentResponse(BaseModel):
    id: int
    policy_id: int
    amount: float
    payment_date: date
    payment_method: str
    transaction_id: str
    payment_status: str

    class Config:
        from_attributes = True