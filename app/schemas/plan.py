from pydantic import BaseModel, Field


PLAN_TYPES = {
    "Life",
    "Health",
    "Vehicle",
    "Property",
    "Travel",
}

PLAN_STATUSES = {
    "Active",
    "Inactive",
}


class PlanCreate(BaseModel):
    plan_name: str = Field(..., min_length=2, max_length=150)
    plan_type: str
    description: str | None = None

    coverage_amount: float = Field(..., gt=0)
    premium_amount: float = Field(..., gt=0)

    duration_years: int = Field(..., gt=0)

    eligibility_age_min: int = Field(..., ge=0)
    eligibility_age_max: int = Field(..., ge=0)

    status: str = "Active"


class PlanUpdate(BaseModel):
    plan_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    plan_type: str | None = None
    description: str | None = None

    coverage_amount: float | None = Field(
        default=None,
        gt=0,
    )

    premium_amount: float | None = Field(
        default=None,
        gt=0,
    )

    duration_years: int | None = Field(
        default=None,
        gt=0,
    )

    eligibility_age_min: int | None = Field(
        default=None,
        ge=0,
    )

    eligibility_age_max: int | None = Field(
        default=None,
        ge=0,
    )

    status: str | None = None


class PlanResponse(BaseModel):
    id: int
    plan_name: str
    plan_type: str
    description: str | None

    coverage_amount: float
    premium_amount: float

    duration_years: int

    eligibility_age_min: int
    eligibility_age_max: int

    status: str

    class Config:
        from_attributes = True