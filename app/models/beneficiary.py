from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.database import Base


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

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

    name = Column(
        String(150),
        nullable=False,
    )

    relationship = Column(
        String(100),
        nullable=False,
    )

    percentage = Column(
        Float,
        nullable=False,
    )

    phone = Column(
        String(30),
        nullable=False,
    )

    identification_number = Column(
        String(100),
        nullable=False,
    )