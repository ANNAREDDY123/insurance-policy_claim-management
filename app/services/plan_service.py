from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.repositories.plan_repository import PlanRepository


class PlanService:

    @staticmethod
    def get_plan(
        db: Session,
        plan_id: int,
    ):
        return PlanRepository.get_by_id(
            db=db,
            plan_id=plan_id,
        )

    @staticmethod
    def get_plan_by_name(
        db: Session,
        plan_name: str,
    ):
        return PlanRepository.get_by_name(
            db=db,
            plan_name=plan_name,
        )

    @staticmethod
    def get_plan_by_name_excluding_id(
        db: Session,
        plan_name: str,
        plan_id: int,
    ):
        return PlanRepository.get_by_name_excluding_id(
            db=db,
            plan_name=plan_name,
            plan_id=plan_id,
        )

    @staticmethod
    def get_plans(
        db: Session,
        plan_type: str | None = None,
        status: str | None = None,
    ):
        return PlanRepository.get_all(
            db=db,
            plan_type=plan_type,
            status=status,
        )

    @staticmethod
    def create_plan(
        db: Session,
        plan: Plan,
    ):
        return PlanRepository.create(
            db=db,
            plan=plan,
        )

    @staticmethod
    def update_plan(
        db: Session,
        plan: Plan,
    ):
        return PlanRepository.update(
            db=db,
            plan=plan,
        )

    @staticmethod
    def delete_plan(
        db: Session,
        plan: Plan,
    ):
        return PlanRepository.delete(
            db=db,
            plan=plan,
        )

    @staticmethod
    def get_plan_query(
        db: Session,
    ):
        return PlanRepository.get_query(
            db=db,
        )