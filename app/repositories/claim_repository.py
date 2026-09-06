from datetime import date

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.customer import Customer
from app.models.policy import Policy


class ClaimRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        claim_id: int,
    ):
        return (
            db.query(Claim)
            .filter(Claim.id == claim_id)
            .first()
        )

    @staticmethod
    def get_policy_by_id(
        db: Session,
        policy_id: int,
    ):
        return (
            db.query(Policy)
            .filter(Policy.id == policy_id)
            .first()
        )

    @staticmethod
    def get_customer_by_id(
        db: Session,
        customer_id: int,
    ):
        return (
            db.query(Customer)
            .filter(Customer.id == customer_id)
            .first()
        )

    @staticmethod
    def get_by_claim_number(
        db: Session,
        claim_number: str,
    ):
        return (
            db.query(Claim)
            .filter(
                Claim.claim_number == claim_number
            )
            .first()
        )

    @staticmethod
    def get_by_policy_and_incident_date(
        db: Session,
        policy_id: int,
        incident_date: date,
    ):
        return (
            db.query(Claim)
            .filter(
                Claim.policy_id == policy_id,
                Claim.incident_date == incident_date,
            )
            .first()
        )

    @staticmethod
    def get_by_policy_and_incident_date_excluding_id(
        db: Session,
        policy_id: int,
        incident_date: date,
        claim_id: int,
    ):
        return (
            db.query(Claim)
            .filter(
                Claim.policy_id == policy_id,
                Claim.incident_date == incident_date,
                Claim.id != claim_id,
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        status: str | None = None,
        claim_type: str | None = None,
        customer_id: int | None = None,
        policy_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        amount_min: float | None = None,
        amount_max: float | None = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "id",
        sort_order: str = "asc",
    ):
        allowed_sort_fields = {
            "id": Claim.id,
            "claim_number": Claim.claim_number,
            "claim_type": Claim.claim_type,
            "incident_date": Claim.incident_date,
            "claim_amount": Claim.claim_amount,
            "status": Claim.status,
        }

        query = db.query(Claim)

        if status is not None:
            query = query.filter(
                Claim.status == status
            )

        if claim_type is not None:
            query = query.filter(
                Claim.claim_type == claim_type
            )

        if customer_id is not None:
            query = query.filter(
                Claim.customer_id == customer_id
            )

        if policy_id is not None:
            query = query.filter(
                Claim.policy_id == policy_id
            )

        if date_from is not None:
            query = query.filter(
                Claim.incident_date >= date_from
            )

        if date_to is not None:
            query = query.filter(
                Claim.incident_date <= date_to
            )

        if amount_min is not None:
            query = query.filter(
                Claim.claim_amount >= amount_min
            )

        if amount_max is not None:
            query = query.filter(
                Claim.claim_amount <= amount_max
            )

        sort_column = allowed_sort_fields[sort_by]

        if sort_order == "desc":
            query = query.order_by(
                desc(sort_column)
            )
        else:
            query = query.order_by(
                asc(sort_column)
            )

        offset = (page - 1) * limit

        return (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        claim: Claim,
    ):
        db.add(claim)
        db.commit()
        db.refresh(claim)

        return claim

    @staticmethod
    def update(
        db: Session,
        claim: Claim,
    ):
        db.commit()
        db.refresh(claim)

        return claim