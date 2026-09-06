from datetime import date

from pydantic import BaseModel, Field


POLICY_STATUSES = {
    "Pending",
    "Active",
    "Expired",
    "Cancelled",
    "Suspended",
}


class PolicyCreate(BaseModel):
    policy_number: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    customer_id: int
    plan_id: int
    agent_id: int

    start_date: date
    end_date: date

    coverage_amount: float = Field(
        ...,
        gt=0,
    )

    premium_amount: float = Field(
        ...,
        gt=0,
    )

    policy_status: str = "Pending"


class PolicyUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    coverage_amount: float | None = Field(
        default=None,
        gt=0,
    )

    premium_amount: float | None = Field(
        default=None,
        gt=0,
    )

    policy_status: str | None = None


class PolicyResponse(BaseModel):
    id: int
    policy_number: str
    customer_id: int
    plan_id: int
    agent_id: int
    start_date: date
    end_date: date
    coverage_amount: float
    premium_amount: float
    policy_status: str

    class Config:
        from_attributes = True