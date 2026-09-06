from datetime import datetime

from pydantic import BaseModel, Field


class ClaimAssessmentCreate(BaseModel):
    claim_id: int
    assessment_status: str = Field(
        default="Pending",
        min_length=2,
        max_length=50,
    )
    approved_amount: float | None = Field(
        default=None,
        ge=0,
    )
    remarks: str | None = Field(
        default=None,
        max_length=1000,
    )


class ClaimAssessmentUpdate(BaseModel):
    assessment_status: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )
    approved_amount: float | None = Field(
        default=None,
        ge=0,
    )
    remarks: str | None = Field(
        default=None,
        max_length=1000,
    )


class ClaimAssessmentResponse(BaseModel):
    id: int
    claim_id: int
    assessor_id: int
    assessment_status: str
    approved_amount: float | None
    remarks: str | None
    assessed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True