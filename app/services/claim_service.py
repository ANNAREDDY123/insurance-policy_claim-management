from datetime import date

from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.repositories.claim_repository import ClaimRepository


class ClaimService:

    @staticmethod
    def get_claim(
        db: Session,
        claim_id: int,
    ):
        return ClaimRepository.get_by_id(
            db=db,
            claim_id=claim_id,
        )

    @staticmethod
    def get_policy(
        db: Session,
        policy_id: int,
    ):
        return ClaimRepository.get_policy_by_id(
            db=db,
            policy_id=policy_id,
        )

    @staticmethod
    def get_customer(
        db: Session,
        customer_id: int,
    ):
        return ClaimRepository.get_customer_by_id(
            db=db,
            customer_id=customer_id,
        )

    @staticmethod
    def get_claim_by_number(
        db: Session,
        claim_number: str,
    ):
        return ClaimRepository.get_by_claim_number(
            db=db,
            claim_number=claim_number,
        )

    @staticmethod
    def get_claim_by_policy_and_incident_date(
        db: Session,
        policy_id: int,
        incident_date: date,
    ):
        return (
            ClaimRepository
            .get_by_policy_and_incident_date(
                db=db,
                policy_id=policy_id,
                incident_date=incident_date,
            )
        )

    @staticmethod
    def get_claim_by_policy_and_incident_date_excluding_id(
        db: Session,
        policy_id: int,
        incident_date: date,
        claim_id: int,
    ):
        return (
            ClaimRepository
            .get_by_policy_and_incident_date_excluding_id(
                db=db,
                policy_id=policy_id,
                incident_date=incident_date,
                claim_id=claim_id,
            )
        )

    @staticmethod
    def get_claims(
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
        return ClaimRepository.get_all(
            db=db,
            status=status,
            claim_type=claim_type,
            customer_id=customer_id,
            policy_id=policy_id,
            date_from=date_from,
            date_to=date_to,
            amount_min=amount_min,
            amount_max=amount_max,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    @staticmethod
    def create_claim(
        db: Session,
        claim: Claim,
    ):
        return ClaimRepository.create(
            db=db,
            claim=claim,
        )

    @staticmethod
    def update_claim(
        db: Session,
        claim: Claim,
    ):
        return ClaimRepository.update(
            db=db,
            claim=claim,
        )