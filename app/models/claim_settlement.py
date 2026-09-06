from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class ClaimSettlement(Base):
    __tablename__ = "claim_settlements"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    claim_id = Column(
        Integer,
        ForeignKey("claims.id"),
        nullable=False,
    )

    settled_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    settlement_amount = Column(
        Float,
        nullable=False,
    )

    settlement_status = Column(
        String(50),
        nullable=False,
        default="Pending",
    )

    payment_reference = Column(
        String(100),
        nullable=True,
    )

    remarks = Column(
        Text,
        nullable=True,
    )

    settled_at = Column(
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