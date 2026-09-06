from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    policy_id = Column(
        Integer,
        ForeignKey("policies.id"),
        nullable=False,
        index=True,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    payment_date = Column(
        Date,
        nullable=False,
    )

    payment_method = Column(
        String(30),
        nullable=False,
    )

    transaction_id = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    payment_status = Column(
        String(30),
        nullable=False,
        default="Pending",
        index=True,
    )