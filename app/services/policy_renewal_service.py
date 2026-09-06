from sqlalchemy.orm import Session

from app.models.policy_renewal import PolicyRenewal
from app.repositories.policy_renewal_repository import (
    PolicyRenewalRepository,
)


class PolicyRenewalService:

    @staticmethod
    def get_latest_renewal(
        db: Session,
        previous_policy_id: int,
    ):
        return (
            PolicyRenewalRepository
            .get_by_previous_policy_id(
                db=db,
                previous_policy_id=previous_policy_id,
            )
        )

    @staticmethod
    def get_policy_renewal_history(
        db: Session,
        previous_policy_id: int,
    ):
        return (
            PolicyRenewalRepository
            .get_all_by_previous_policy_id(
                db=db,
                previous_policy_id=previous_policy_id,
            )
        )

    @staticmethod
    def get_renewal_by_renewed_policy_id(
        db: Session,
        renewed_policy_id: int,
    ):
        return (
            PolicyRenewalRepository
            .get_by_renewed_policy_id(
                db=db,
                renewed_policy_id=renewed_policy_id,
            )
        )

    @staticmethod
    def create_policy_renewal(
        db: Session,
        renewal: PolicyRenewal,
    ):
        return PolicyRenewalRepository.create(
            db=db,
            renewal=renewal,
        )