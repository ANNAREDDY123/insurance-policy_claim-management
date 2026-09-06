from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:

    @staticmethod
    def get_by_id(db: Session, customer_id: int):
        return (
            db.query(Customer)
            .filter(
                Customer.id == customer_id,
                Customer.is_deleted == False,
            )
            .first()
        )

    @staticmethod
    def get_by_email(db: Session, email: str):
        return (
            db.query(Customer)
            .filter(
                Customer.email == email,
                Customer.is_deleted == False,
            )
            .first()
        )

    @staticmethod
    def get_by_email_excluding_id(
        db: Session,
        email: str,
        customer_id: int,
    ):
        return (
            db.query(Customer)
            .filter(
                Customer.email == email,
                Customer.id != customer_id,
                Customer.is_deleted == False,
            )
            .first()
        )

    @staticmethod
    def get_by_identification_number(
        db: Session,
        identification_number: str,
    ):
        return (
            db.query(Customer)
            .filter(
                Customer.identification_number == identification_number,
                Customer.is_deleted == False,
            )
            .first()
        )

    @staticmethod
    def get_by_identification_number_excluding_id(
        db: Session,
        identification_number: str,
        customer_id: int,
    ):
        return (
            db.query(Customer)
            .filter(
                Customer.identification_number == identification_number,
                Customer.id != customer_id,
                Customer.is_deleted == False,
            )
            .first()
        )

    @staticmethod
    def get_all(db: Session):
        return (
            db.query(Customer)
            .filter(Customer.is_deleted == False)
            .all()
        )

    @staticmethod
    def create(db: Session, customer: Customer):
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def delete(db: Session, customer: Customer):
        customer.is_deleted = True
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_query(db: Session):
        return (
            db.query(Customer)
            .filter(Customer.is_deleted == False)
        )

    @staticmethod
    def update(
        db: Session,
        customer: Customer,
    ):
        db.commit()
        db.refresh(customer)
        return customer