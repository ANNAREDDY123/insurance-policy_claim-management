from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository


class CustomerService:

    @staticmethod
    def get_customer(
        db: Session,
        customer_id: int,
    ):
        return CustomerRepository.get_by_id(
            db=db,
            customer_id=customer_id,
        )

    @staticmethod
    def get_customer_by_email(
        db: Session,
        email: str,
    ):
        return CustomerRepository.get_by_email(
            db=db,
            email=email,
        )

    @staticmethod
    def get_customer_by_email_excluding_id(
        db: Session,
        email: str,
        customer_id: int,
    ):
        return CustomerRepository.get_by_email_excluding_id(
            db=db,
            email=email,
            customer_id=customer_id,
        )

    @staticmethod
    def get_customer_by_identification_number(
        db: Session,
        identification_number: str,
    ):
        return CustomerRepository.get_by_identification_number(
            db=db,
            identification_number=identification_number,
        )

    @staticmethod
    def get_customer_by_identification_number_excluding_id(
        db: Session,
        identification_number: str,
        customer_id: int,
    ):
        return (
            CustomerRepository
            .get_by_identification_number_excluding_id(
                db=db,
                identification_number=identification_number,
                customer_id=customer_id,
            )
        )

    @staticmethod
    def get_customers(
        db: Session,
    ):
        return CustomerRepository.get_all(
            db=db,
        )

    @staticmethod
    def create_customer(
        db: Session,
        customer: Customer,
    ):
        return CustomerRepository.create(
            db=db,
            customer=customer,
        )

    @staticmethod
    def delete_customer(
        db: Session,
        customer: Customer,
    ):
        return CustomerRepository.delete(
            db=db,
            customer=customer,
        )

    @staticmethod
    def get_customer_query(
        db: Session,
    ):
        return CustomerRepository.get_query(
            db=db,
        )

    @staticmethod
    def update_customer(
        db: Session,
        customer: Customer,
    ):
        return CustomerRepository.update(
            db=db,
            customer=customer,
        )