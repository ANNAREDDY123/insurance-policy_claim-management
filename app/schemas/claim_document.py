from datetime import datetime

from pydantic import BaseModel, Field


VERIFICATION_STATUSES = {
    "Pending",
    "Verified",
    "Rejected",
}


class ClaimDocumentCreate(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    file_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    file_path: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class ClaimDocumentUpdate(BaseModel):
    document_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    # Existing tests send this field
    status: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )


class ClaimDocumentVerify(BaseModel):
    verification_status: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )


class ClaimDocumentResponse(BaseModel):
    id: int
    claim_id: int
    document_type: str
    file_name: str
    file_path: str
    description: str | None

    # Level 8 verification field
    verification_status: str

    # Existing test compatibility
    status: str

    uploaded_at: datetime

    class Config:
        from_attributes = True