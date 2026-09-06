from sqlalchemy import Column, Integer, String, Text, Float

from app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)

    plan_name = Column(String(150), nullable=False, unique=True)
    plan_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    coverage_amount = Column(Float, nullable=False)
    premium_amount = Column(Float, nullable=False)

    duration_years = Column(Integer, nullable=False)

    eligibility_age_min = Column(Integer, nullable=False)
    eligibility_age_max = Column(Integer, nullable=False)

    status = Column(String(20), nullable=False, default="Active")