from datetime import date

from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.repositories.policy_repository import PolicyRepository


class PolicyService:

    @staticmethod
    def get_policy(
        db: Session,
        policy_id: int,
    ):
        return PolicyRepository.get_by_id(
            db=db,
            policy_id=policy_id,
        )

    @staticmethod
    def get_customer(
        db: Session,
        customer_id: int,
    ):
        return PolicyRepository.get_customer_by_id(
            db=db,
            customer_id=customer_id,
        )

    @staticmethod
    def get_plan(
        db: Session,
        plan_id: int,
    ):
        return PolicyRepository.get_plan_by_id(
            db=db,
            plan_id=plan_id,
        )

    @staticmethod
    def get_user(
        db: Session,
        user_id: int,
    ):
        return PolicyRepository.get_user_by_id(
            db=db,
            user_id=user_id,
        )

    @staticmethod
    def get_policy_by_number(
        db: Session,
        policy_number: str,
    ):
        return PolicyRepository.get_by_policy_number(
            db=db,
            policy_number=policy_number,
        )

    @staticmethod
    def get_active_overlapping_policy(
        db: Session,
        customer_id: int,
        plan_id: int,
        start_date: date,
        end_date: date,
        exclude_policy_id: int | None = None,
    ):
        return PolicyRepository.get_active_overlapping_policy(
            db=db,
            customer_id=customer_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            exclude_policy_id=exclude_policy_id,
        )

    @staticmethod
    def get_policies(
        db: Session,
        status: str | None = None,
        customer_id: int | None = None,
        plan_id: int | None = None,
        agent_id: int | None = None,
        plan_type: str | None = None,
        customer: str | None = None,
        expiry_date: date | None = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "id",
        sort_order: str = "asc",
    ):
        return PolicyRepository.get_all(
            db=db,
            status=status,
            customer_id=customer_id,
            plan_id=plan_id,
            agent_id=agent_id,
            plan_type=plan_type,
            customer=customer,
            expiry_date=expiry_date,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    @staticmethod
    def create_policy(
        db: Session,
        policy: Policy,
    ):
        return PolicyRepository.create(
            db=db,
            policy=policy,
        )

    @staticmethod
    def update_policy(
        db: Session,
        policy: Policy,
    ):
        return PolicyRepository.update(
            db=db,
            policy=policy,
        )

    @staticmethod
    def delete_policy(
        db: Session,
        policy: Policy,
    ):
        return PolicyRepository.delete(
            db=db,
            policy=policy,
        )