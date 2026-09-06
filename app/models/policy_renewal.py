from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.database import Base


class PolicyRenewal(Base):
    __tablename__ = "policy_renewals"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    previous_policy_id = Column(
        Integer,
        ForeignKey("policies.id"),
        nullable=False,
        index=True,
    )

    renewed_policy_id = Column(
        Integer,
        ForeignKey("policies.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    renewal_date = Column(
        Date,
        nullable=False,
    )

    previous_end_date = Column(
        Date,
        nullable=False,
    )

    new_start_date = Column(
        Date,
        nullable=False,
    )

    new_end_date = Column(
        Date,
        nullable=False,
    )

    renewed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="Completed",
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