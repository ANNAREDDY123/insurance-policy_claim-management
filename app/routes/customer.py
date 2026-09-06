from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customer_service import CustomerService
from app.utils.dependencies import get_current_user, require_roles


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


CUSTOMER_ROLES = {
    "Super Admin",
    "Insurance Agent",
    "Claims Officer",
    "Finance Officer",
}


def calculate_age(date_of_birth: date) -> int:
    today = date.today()

    age = (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (date_of_birth.month, date_of_birth.day)
        )
    )

    return age


def validate_date_of_birth(date_of_birth: date):
    if date_of_birth > date.today():
        raise HTTPException(
            status_code=400,
            detail="Date of birth cannot be in the future",
        )

    age = calculate_age(date_of_birth)

    if age < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid date of birth",
        )


def get_customer_or_404(
    db: Session,
    customer_id: int,
):
    customer = CustomerService.get_customer(
        db=db,
        customer_id=customer_id,
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.post(
    "",
    response_model=CustomerResponse,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    validate_date_of_birth(
        customer_data.date_of_birth
    )

    existing_email = (
        CustomerService.get_customer_by_email(
            db=db,
            email=customer_data.email,
        )
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Customer email already exists",
        )

    existing_identification = (
        CustomerService
        .get_customer_by_identification_number(
            db=db,
            identification_number=(
                customer_data.identification_number
            ),
        )
    )

    if existing_identification:
        raise HTTPException(
            status_code=409,
            detail="Identification number already exists",
        )

    customer = Customer(
        full_name=customer_data.full_name,
        email=customer_data.email,
        phone=customer_data.phone,
        date_of_birth=customer_data.date_of_birth,
        address=customer_data.address,
        identification_number=(
            customer_data.identification_number
        ),
        occupation=customer_data.occupation,
        is_deleted=False,
    )

    try:
        customer = CustomerService.create_customer(
            db=db,
            customer=customer,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Customer email or identification "
                "number already exists"
            ),
        )

    return customer


@router.get(
    "",
    response_model=list[CustomerResponse],
)
def get_customers(
    name: str | None = Query(
        default=None,
        min_length=1,
    ),
    email: str | None = None,
    identification_number: str | None = None,
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="id",
        pattern="^(id|full_name|email|date_of_birth)$",
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    query = CustomerService.get_customer_query(
        db=db
    )

    if name is not None:
        query = query.filter(
            Customer.full_name.ilike(
                f"%{name}%"
            )
        )

    if email is not None:
        query = query.filter(
            Customer.email == email
        )

    if identification_number is not None:
        query = query.filter(
            Customer.identification_number
            == identification_number
        )

    sort_column = getattr(
        Customer,
        sort_by,
    )

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc()
        )
    else:
        query = query.order_by(
            sort_column.asc()
        )

    offset = (page - 1) * limit

    return (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_customer_or_404(
        db=db,
        customer_id=customer_id,
    )


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    customer = get_customer_or_404(
        db=db,
        customer_id=customer_id,
    )

    if customer_data.date_of_birth is not None:
        validate_date_of_birth(
            customer_data.date_of_birth
        )

    # Check email using service layer
    if customer_data.email is not None:
        existing_email = (
            CustomerService
            .get_customer_by_email_excluding_id(
                db=db,
                email=customer_data.email,
                customer_id=customer.id,
            )
        )

        if existing_email:
            raise HTTPException(
                status_code=409,
                detail="Customer email already exists",
            )

        customer.email = customer_data.email

    # Check identification number using service layer
    if (
        customer_data.identification_number
        is not None
    ):
        existing_identification = (
            CustomerService
            .get_customer_by_identification_number_excluding_id(
                db=db,
                identification_number=(
                    customer_data.identification_number
                ),
                customer_id=customer.id,
            )
        )

        if existing_identification:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Identification number "
                    "already exists"
                ),
            )

        customer.identification_number = (
            customer_data.identification_number
        )

    if customer_data.full_name is not None:
        customer.full_name = (
            customer_data.full_name
        )

    if customer_data.phone is not None:
        customer.phone = customer_data.phone

    if customer_data.date_of_birth is not None:
        customer.date_of_birth = (
            customer_data.date_of_birth
        )

    if customer_data.address is not None:
        customer.address = (
            customer_data.address
        )

    if customer_data.occupation is not None:
        customer.occupation = (
            customer_data.occupation
        )

    try:
        customer = CustomerService.update_customer(
            db=db,
            customer=customer,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Customer email or identification "
                "number already exists"
            ),
        )

    return customer


@router.delete(
    "/{customer_id}",
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Super Admin")
    ),
):
    customer = get_customer_or_404(
        db=db,
        customer_id=customer_id,
    )

    CustomerService.delete_customer(
        db=db,
        customer=customer,
    )

    return {
        "message": "Customer deleted successfully"
    }