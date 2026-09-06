from datetime import date

from pydantic import BaseModel, Field


CLAIM_STATUSES = {
    "Submitted",
    "Under Review",
    "Documents Required",
    "Approved",
    "Rejected",
    "Settled",
}


class ClaimCreate(BaseModel):
    claim_number: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    policy_id: int
    customer_id: int

    claim_type: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    incident_date: date

    claim_amount: float = Field(
        ...,
        gt=0,
    )

    description: str = Field(
        ...,
        min_length=5,
    )

    status: str = "Submitted"


class ClaimUpdate(BaseModel):
    claim_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    incident_date: date | None = None

    claim_amount: float | None = Field(
        default=None,
        gt=0,
    )

    description: str | None = Field(
        default=None,
        min_length=5,
    )

    status: str | None = None


class ClaimResponse(BaseModel):
    id: int
    claim_number: str
    policy_id: int
    customer_id: int
    claim_type: str
    incident_date: date
    claim_amount: float
    description: str
    status: str

    class Config:
        from_attributes = True