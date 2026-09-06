from sqlalchemy.orm import Session

from app.models.plan import Plan


class PlanRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        plan_id: int,
    ):
        return (
            db.query(Plan)
            .filter(Plan.id == plan_id)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        plan_name: str,
    ):
        return (
            db.query(Plan)
            .filter(Plan.plan_name == plan_name)
            .first()
        )

    @staticmethod
    def get_by_name_excluding_id(
        db: Session,
        plan_name: str,
        plan_id: int,
    ):
        return (
            db.query(Plan)
            .filter(
                Plan.plan_name == plan_name,
                Plan.id != plan_id,
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
        plan_type: str | None = None,
        status: str | None = None,
    ):
        query = db.query(Plan)

        if plan_type is not None:
            query = query.filter(
                Plan.plan_type == plan_type
            )

        if status is not None:
            query = query.filter(
                Plan.status == status
            )

        return (
            query
            .order_by(Plan.id)
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        plan: Plan,
    ):
        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def update(
        db: Session,
        plan: Plan,
    ):
        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def delete(
        db: Session,
        plan: Plan,
    ):
        db.delete(plan)
        db.commit()

        return plan

    @staticmethod
    def get_query(
        db: Session,
    ):
        return db.query(Plan)