from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.repositories.payment_repository import (
    PaymentRepository,
)


class PaymentService:

    @staticmethod
    def get_payment(
        db: Session,
        payment_id: int,
    ):
        return PaymentRepository.get_by_id(
            db=db,
            payment_id=payment_id,
        )

    @staticmethod
    def get_payment_by_transaction_id(
        db: Session,
        transaction_id: str,
    ):
        return (
            PaymentRepository.get_by_transaction_id(
                db=db,
                transaction_id=transaction_id,
            )
        )

    @staticmethod
    def get_policy_payments(
        db: Session,
        policy_id: int,
    ):
        return PaymentRepository.get_by_policy_id(
            db=db,
            policy_id=policy_id,
        )

    @staticmethod
    def get_payment_query(
        db: Session,
    ):
        return PaymentRepository.get_query(
            db=db,
        )

    @staticmethod
    def create_payment(
        db: Session,
        payment: Payment,
    ):
        return PaymentRepository.create(
            db=db,
            payment=payment,
        )