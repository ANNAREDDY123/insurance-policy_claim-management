from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

from app.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)

    policy_number = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    plan_id = Column(
        Integer,
        ForeignKey("plans.id"),
        nullable=False,
        index=True,
    )

    agent_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    start_date = Column(
        Date,
        nullable=False,
    )

    end_date = Column(
        Date,
        nullable=False,
    )

    coverage_amount = Column(
        Float,
        nullable=False,
    )

    premium_amount = Column(
        Float,
        nullable=False,
    )

    policy_status = Column(
        String(30),
        nullable=False,
        default="Pending",
        index=True,
    )