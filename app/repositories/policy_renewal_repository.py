from sqlalchemy.orm import Session

from app.models.policy_renewal import PolicyRenewal


class PolicyRenewalRepository:

    @staticmethod
    def get_by_previous_policy_id(
        db: Session,
        previous_policy_id: int,
    ):
        return (
            db.query(PolicyRenewal)
            .filter(
                PolicyRenewal.previous_policy_id
                == previous_policy_id
            )
            .order_by(
                PolicyRenewal.id.desc()
            )
            .first()
        )

    @staticmethod
    def get_all_by_previous_policy_id(
        db: Session,
        previous_policy_id: int,
    ):
        return (
            db.query(PolicyRenewal)
            .filter(
                PolicyRenewal.previous_policy_id
                == previous_policy_id
            )
            .order_by(
                PolicyRenewal.id.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_renewed_policy_id(
        db: Session,
        renewed_policy_id: int,
    ):
        return (
            db.query(PolicyRenewal)
            .filter(
                PolicyRenewal.renewed_policy_id
                == renewed_policy_id
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        renewal: PolicyRenewal,
    ):
        db.add(renewal)
        db.commit()
        db.refresh(renewal)

        return renewal