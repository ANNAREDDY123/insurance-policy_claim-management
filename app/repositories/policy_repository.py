from datetime import date

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.plan import Plan
from app.models.policy import Policy
from app.models.user import User


class PolicyRepository:

    @staticmethod
    def get_by_id(
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
    def get_plan_by_id(
        db: Session,
        plan_id: int,
    ):
        return (
            db.query(Plan)
            .filter(Plan.id == plan_id)
            .first()
        )

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int,
    ):
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_by_policy_number(
        db: Session,
        policy_number: str,
    ):
        return (
            db.query(Policy)
            .filter(
                Policy.policy_number == policy_number
            )
            .first()
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
        query = (
            db.query(Policy)
            .filter(
                Policy.customer_id == customer_id,
                Policy.plan_id == plan_id,
                Policy.policy_status == "Active",
                Policy.start_date < end_date,
                Policy.end_date > start_date,
            )
        )

        if exclude_policy_id is not None:
            query = query.filter(
                Policy.id != exclude_policy_id
            )

        return query.first()

    @staticmethod
    def get_all(
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
        allowed_sort_fields = {
            "id": Policy.id,
            "policy_number": Policy.policy_number,
            "start_date": Policy.start_date,
            "end_date": Policy.end_date,
            "coverage_amount": Policy.coverage_amount,
            "premium_amount": Policy.premium_amount,
            "policy_status": Policy.policy_status,
        }

        query = (
            db.query(Policy)
            .join(
                Plan,
                Policy.plan_id == Plan.id,
            )
            .join(
                Customer,
                Policy.customer_id == Customer.id,
            )
        )

        if status is not None:
            query = query.filter(
                Policy.policy_status == status
            )

        if customer_id is not None:
            query = query.filter(
                Policy.customer_id == customer_id
            )

        if plan_id is not None:
            query = query.filter(
                Policy.plan_id == plan_id
            )

        if agent_id is not None:
            query = query.filter(
                Policy.agent_id == agent_id
            )

        if plan_type is not None:
            query = query.filter(
                Plan.plan_type == plan_type
            )

        if customer is not None:
            customer_search = f"%{customer}%"

            query = query.filter(
                or_(
                    Customer.full_name.ilike(
                        customer_search
                    ),
                    Customer.email.ilike(
                        customer_search
                    ),
                )
            )

        if expiry_date is not None:
            query = query.filter(
                Policy.end_date == expiry_date
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
        policy: Policy,
    ):
        db.add(policy)
        db.commit()
        db.refresh(policy)

        return policy

    @staticmethod
    def update(
        db: Session,
        policy: Policy,
    ):
        db.commit()
        db.refresh(policy)

        return policy

    @staticmethod
    def delete(
        db: Session,
        policy: Policy,
    ):
        db.delete(policy)
        db.commit()

        return policy