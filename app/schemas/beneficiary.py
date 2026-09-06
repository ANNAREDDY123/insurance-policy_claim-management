from pydantic import BaseModel, Field


class BeneficiaryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    relationship: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    percentage: float = Field(
        ...,
        gt=0,
        le=100,
    )

    phone: str = Field(
        ...,
        min_length=7,
        max_length=30,
    )

    identification_number: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )


class BeneficiaryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    relationship: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    percentage: float | None = Field(
        default=None,
        gt=0,
        le=100,
    )

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=30,
    )

    identification_number: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )


class BeneficiaryResponse(BaseModel):
    id: int
    policy_id: int
    name: str
    relationship: str
    percentage: float
    phone: str
    identification_number: str

    class Config:
        from_attributes = True