from datetime import datetime

from pydantic import BaseModel, Field


SETTLEMENT_STATUSES = {
    "Pending",
    "Processing",
    "Completed",
    "Failed",
}


class ClaimSettlementCreate(BaseModel):
    claim_id: int

    settlement_amount: float = Field(
        ...,
        gt=0,
    )

    settlement_status: str = Field(
        default="Pending",
        min_length=2,
        max_length=50,
    )

    payment_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    remarks: str | None = Field(
        default=None,
        max_length=1000,
    )


class ClaimSettlementUpdate(BaseModel):
    settlement_amount: float | None = Field(
        default=None,
        gt=0,
    )

    settlement_status: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    payment_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    remarks: str | None = Field(
        default=None,
        max_length=1000,
    )


class ClaimSettlementResponse(BaseModel):
    id: int
    claim_id: int
    settled_by: int
    settlement_amount: float
    settlement_status: str
    payment_reference: str | None
    remarks: str | None
    settled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True