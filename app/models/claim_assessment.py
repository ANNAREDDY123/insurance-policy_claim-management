from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class ClaimAssessment(Base):
    __tablename__ = "claim_assessments"

    id = Column(Integer, primary_key=True, index=True)

    claim_id = Column(
        Integer,
        ForeignKey("claims.id"),
        nullable=False,
    )

    assessor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    assessment_status = Column(
        String(50),
        nullable=False,
        default="Pending",
    )

    approved_amount = Column(
        Float,
        nullable=True,
    )

    remarks = Column(
        Text,
        nullable=True,
    )

    assessed_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )