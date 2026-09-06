from datetime import date

from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str = Field(
        ...,
        min_length=7,
        max_length=30,
    )

    date_of_birth: date

    address: str | None = Field(
        default=None,
        max_length=500,
    )

    identification_number: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    occupation: str | None = Field(
        default=None,
        max_length=150,
    )


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=30,
    )

    date_of_birth: date | None = None

    address: str | None = Field(
        default=None,
        max_length=500,
    )

    identification_number: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    occupation: str | None = Field(
        default=None,
        max_length=150,
    )


class CustomerResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    address: str | None
    identification_number: str
    occupation: str | None

    class Config:
        from_attributes = True