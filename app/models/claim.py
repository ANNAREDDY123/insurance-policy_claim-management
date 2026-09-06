from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    claim_number = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    policy_id = Column(
        Integer,
        ForeignKey("policies.id"),
        nullable=False,
        index=True,
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    claim_type = Column(
        String(100),
        nullable=False,
    )

    incident_date = Column(
        Date,
        nullable=False,
    )

    claim_amount = Column(
        Float,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="Submitted",
        index=True,
    )