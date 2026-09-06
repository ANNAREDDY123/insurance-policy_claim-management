from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.models.policy import Policy
from app.models.user import User
from app.schemas.payment import (
    PAYMENT_METHODS,
    PAYMENT_STATUSES,
    PaymentCreate,
    PaymentResponse,
)
from app.services.notification_tasks import send_notification_background
from app.utils.dependencies import get_current_user, require_roles


router = APIRouter(
    tags=["Payments"],
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_policy_or_404(
    db: Session,
    policy_id: int,
):
    policy = (
        db.query(Policy)
        .filter(Policy.id == policy_id)
        .first()
    )

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Policy not found",
        )

    return policy


def get_payment_or_404(
    db: Session,
    payment_id: int,
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment


def validate_payment_method(
    payment_method: str,
):
    if payment_method not in PAYMENT_METHODS:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method",
        )


def validate_payment_status(
    payment_status: str,
):
    if payment_status not in PAYMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status",
        )


def check_transaction_id(
    db: Session,
    transaction_id: str,
):
    existing = (
        db.query(Payment)
        .filter(
            Payment.transaction_id == transaction_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Transaction ID already exists",
        )


# =========================================================
# CREATE PREMIUM PAYMENT
# POST /policies/{policy_id}/premium-payment
# =========================================================

@router.post(
    "/policies/{policy_id}/premium-payment",
    response_model=PaymentResponse,
)
def create_premium_payment(
    policy_id: int,
    payment_data: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Finance Officer",
            "Customer",
        )
    ),
):
    policy = get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )

    validate_payment_method(
        payment_data.payment_method
    )

    validate_payment_status(
        payment_data.payment_status
    )

    check_transaction_id(
        db=db,
        transaction_id=payment_data.transaction_id,
    )

    # Premium amount must match policy premium.
    if payment_data.amount != policy.premium_amount:
        raise HTTPException(
            status_code=400,
            detail=(
                "Payment amount must match "
                "the policy premium amount"
            ),
        )

    payment = Payment(
        policy_id=policy_id,
        amount=payment_data.amount,
        payment_date=payment_data.payment_date,
        payment_method=payment_data.payment_method,
        transaction_id=payment_data.transaction_id,
        payment_status=payment_data.payment_status,
    )

    db.add(payment)

    # Only a successful payment can activate
    # a pending policy.
    if (
        payment_data.payment_status == "Success"
        and policy.policy_status == "Pending"
    ):
        policy.policy_status = "Active"

    db.commit()
    db.refresh(payment)

    # -----------------------------------------------------
    # LEVEL 14 - PREMIUM PAYMENT NOTIFICATION
    # -----------------------------------------------------

    if payment_data.payment_status == "Success":
        send_notification_background(
            background_tasks=background_tasks,
            db=db,
            user_id=current_user.id,
            notification_type="PREMIUM_PAYMENT_SUCCESS",
            title="Premium Payment Successful",
            message=(
                f"Your premium payment of "
                f"{payment.amount} for policy "
                f"{policy.policy_number} was successful."
            ),
        )

    return payment


# =========================================================
# GET ALL PAYMENTS
# GET /payments
# LEVEL 12C - FILTERING, PAGINATION & SORTING
# =========================================================

@router.get(
    "/payments",
    response_model=list[PaymentResponse],
)
def get_payments(
    payment_status: str | None = None,
    payment_method: str | None = None,
    policy_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
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
    ),
    sort_order: str = Query(
        default="asc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # -----------------------------------------------------
    # Validate payment status
    # -----------------------------------------------------

    if payment_status is not None:
        validate_payment_status(
            payment_status
        )

    # -----------------------------------------------------
    # Validate payment method
    # -----------------------------------------------------

    if payment_method is not None:
        validate_payment_method(
            payment_method
        )

    # -----------------------------------------------------
    # Validate date range
    # -----------------------------------------------------

    if (
        date_from is not None
        and date_to is not None
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "date_from cannot be later "
                "than date_to"
            ),
        )

    # -----------------------------------------------------
    # Validate sorting
    # -----------------------------------------------------

    allowed_sort_fields = {
        "id": Payment.id,
        "amount": Payment.amount,
        "payment_date": Payment.payment_date,
        "payment_method": Payment.payment_method,
        "payment_status": Payment.payment_status,
        "transaction_id": Payment.transaction_id,
        "policy_id": Payment.policy_id,
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort_by. Allowed values: "
                + ", ".join(
                    allowed_sort_fields.keys()
                )
            ),
        )

    sort_order = sort_order.lower()

    if sort_order not in {
        "asc",
        "desc",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "sort_order must be "
                "'asc' or 'desc'"
            ),
        )

    # -----------------------------------------------------
    # Build query
    # -----------------------------------------------------

    query = db.query(Payment)

    # Payment status filter
    if payment_status is not None:
        query = query.filter(
            Payment.payment_status
            == payment_status
        )

    # Payment method filter
    if payment_method is not None:
        query = query.filter(
            Payment.payment_method
            == payment_method
        )

    # Policy filter
    if policy_id is not None:
        query = query.filter(
            Payment.policy_id == policy_id
        )

    # Payment date range
    if date_from is not None:
        query = query.filter(
            Payment.payment_date >= date_from
        )

    if date_to is not None:
        query = query.filter(
            Payment.payment_date <= date_to
        )

    # -----------------------------------------------------
    # Sorting
    # -----------------------------------------------------

    sort_column = allowed_sort_fields[
        sort_by
    ]

    if sort_order == "desc":
        query = query.order_by(
            desc(sort_column)
        )
    else:
        query = query.order_by(
            asc(sort_column)
        )

    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    offset = (page - 1) * limit

    return (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )


# =========================================================
# GET SINGLE PAYMENT
# GET /payments/{payment_id}
# =========================================================

@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_payment_or_404(
        db=db,
        payment_id=payment_id,
    )


# =========================================================
# GET POLICY PAYMENT HISTORY
# GET /policies/{policy_id}/payments
# =========================================================

@router.get(
    "/policies/{policy_id}/payments",
    response_model=list[PaymentResponse],
)
def get_policy_payments(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )

    return (
        db.query(Payment)
        .filter(
            Payment.policy_id == policy_id
        )
        .order_by(Payment.id)
        .all()
    )