from datetime import date

from sqlalchemy import Boolean, Column, Date, Integer, String

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    full_name = Column(
        String(150),
        nullable=False,
    )

    email = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    phone = Column(
        String(30),
        nullable=False,
    )

    date_of_birth = Column(
        Date,
        nullable=False,
    )

    address = Column(
        String(500),
        nullable=True,
    )

    identification_number = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    occupation = Column(
        String(150),
        nullable=True,
    )

    # Soft Delete
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )