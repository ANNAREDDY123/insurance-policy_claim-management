from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        payment_id: int,
    ):
        return (
            db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

    @staticmethod
    def get_by_transaction_id(
        db: Session,
        transaction_id: str,
    ):
        return (
            db.query(Payment)
            .filter(
                Payment.transaction_id
                == transaction_id
            )
            .first()
        )

    @staticmethod
    def get_by_policy_id(
        db: Session,
        policy_id: int,
    ):
        return (
            db.query(Payment)
            .filter(
                Payment.policy_id == policy_id
            )
            .order_by(Payment.id)
            .all()
        )

    @staticmethod
    def get_query(
        db: Session,
    ):
        return db.query(Payment)

    @staticmethod
    def create(
        db: Session,
        payment: Payment,
    ):
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment