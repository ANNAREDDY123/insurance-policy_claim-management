from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from app.database import Base


class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    claim_id = Column(
        Integer,
        ForeignKey("claims.id"),
        nullable=False,
        index=True,
    )

    document_type = Column(
        String(100),
        nullable=False,
    )

    file_name = Column(
        String(255),
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    description = Column(
        String(500),
        nullable=True,
    )

    # Existing test compatibility
    status = Column(
        String(50),
        nullable=False,
        default="Uploaded",
    )

    # Level 8 verification workflow
    verification_status = Column(
        String(50),
        nullable=False,
        default="Pending",
        index=True,
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )