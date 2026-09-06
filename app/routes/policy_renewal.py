from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.policy import Policy
from app.models.policy_renewal import PolicyRenewal
from app.models.user import User
from app.schemas.policy_renewal import (
    ExpiringPolicyResponse,
    PolicyRenewalResponse,
)
from app.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/policies",
    tags=["Policy Renewal"],
)


# ============================================================
# GET EXPIRING POLICIES
# ============================================================

@router.get(
    "/expiring",
    response_model=list[ExpiringPolicyResponse],
)
def get_expiring_policies(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if days <= 0:
        raise HTTPException(
            status_code=400,
            detail="Days must be greater than 0",
        )

    today = date.today()

    expiry_date = (
        today
        + timedelta(days=days)
    )

    return (
        db.query(Policy)
        .filter(
            Policy.policy_status == "Active",
            Policy.end_date >= today,
            Policy.end_date <= expiry_date,
        )
        .order_by(Policy.end_date)
        .all()
    )


# ============================================================
# RENEW POLICY
# ============================================================

@router.post(
    "/{policy_id}/renew",
    response_model=PolicyRenewalResponse,
    status_code=201,
)
def renew_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    # --------------------------------------------------------
    # GET POLICY
    # --------------------------------------------------------

    policy = (
        db.query(Policy)
        .filter(
            Policy.id == policy_id
        )
        .first()
    )

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Policy not found",
        )

    # --------------------------------------------------------
    # VALIDATE POLICY STATUS
    # --------------------------------------------------------

    if policy.policy_status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled policy cannot be renewed",
        )

    if policy.policy_status == "Suspended":
        raise HTTPException(
            status_code=400,
            detail="Suspended policy cannot be renewed",
        )

    if policy.policy_status not in {
        "Active",
        "Expired",
    }:
        raise HTTPException(
            status_code=400,
            detail="Policy is not eligible for renewal",
        )

    # --------------------------------------------------------
    # PREVENT DUPLICATE RENEWAL
    # --------------------------------------------------------

    existing_renewal = (
        db.query(PolicyRenewal)
        .filter(
            PolicyRenewal.previous_policy_id
            == policy.id
        )
        .first()
    )

    if existing_renewal:
        raise HTTPException(
            status_code=409,
            detail="Policy has already been renewed",
        )

    # --------------------------------------------------------
    # GET CUSTOMER
    # --------------------------------------------------------

    customer = (
        db.query(Customer)
        .filter(
            Customer.id
            == policy.customer_id
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    # --------------------------------------------------------
    # GET PLAN
    # --------------------------------------------------------

    plan = (
        db.query(Plan)
        .filter(
            Plan.id == policy.plan_id
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Insurance plan not found",
        )

    # --------------------------------------------------------
    # PLAN MUST BE ACTIVE
    # --------------------------------------------------------

    if plan.status != "Active":
        raise HTTPException(
            status_code=400,
            detail="Inactive plans cannot be renewed",
        )

    # --------------------------------------------------------
    # CUSTOMER AGE ELIGIBILITY
    # --------------------------------------------------------

    today = date.today()

    age = (
        today.year
        - customer.date_of_birth.year
        - (
            (today.month, today.day)
            < (
                customer.date_of_birth.month,
                customer.date_of_birth.day,
            )
        )
    )

    if age < plan.eligibility_age_min:
        raise HTTPException(
            status_code=400,
            detail=(
                "Customer does not meet minimum "
                "age eligibility"
            ),
        )

    if age > plan.eligibility_age_max:
        raise HTTPException(
            status_code=400,
            detail=(
                "Customer does not meet maximum "
                "age eligibility"
            ),
        )

    # --------------------------------------------------------
    # GENERATE NEW POLICY PERIOD
    # --------------------------------------------------------

    new_start_date = (
        policy.end_date
        + timedelta(days=1)
    )

    policy_duration_days = (
        policy.end_date
        - policy.start_date
    ).days

    new_end_date = (
        new_start_date
        + timedelta(
            days=policy_duration_days
        )
    )

    # --------------------------------------------------------
    # GENERATE UNIQUE POLICY NUMBER
    # --------------------------------------------------------

    renewal_number = 1

    new_policy_number = (
        f"{policy.policy_number}"
        f"-R{renewal_number}"
    )

    while (
        db.query(Policy)
        .filter(
            Policy.policy_number
            == new_policy_number
        )
        .first()
        is not None
    ):
        renewal_number += 1

        new_policy_number = (
            f"{policy.policy_number}"
            f"-R{renewal_number}"
        )

    # --------------------------------------------------------
    # CREATE RENEWED POLICY
    # --------------------------------------------------------

    renewed_policy = Policy(
        policy_number=new_policy_number,
        customer_id=policy.customer_id,
        plan_id=policy.plan_id,
        agent_id=policy.agent_id,
        start_date=new_start_date,
        end_date=new_end_date,
        coverage_amount=policy.coverage_amount,
        premium_amount=policy.premium_amount,
        policy_status="Pending",
    )

    db.add(renewed_policy)

    # Generate ID before creating renewal history
    db.flush()

    # --------------------------------------------------------
    # CREATE RENEWAL HISTORY
    # --------------------------------------------------------

    renewal = PolicyRenewal(
        previous_policy_id=policy.id,
        renewed_policy_id=renewed_policy.id,
        renewal_date=today,
        previous_end_date=policy.end_date,
        new_start_date=new_start_date,
        new_end_date=new_end_date,
        renewed_by=current_user.id,
        status="Completed",
    )

    db.add(renewal)

    # --------------------------------------------------------
    # COMMIT TRANSACTION
    # --------------------------------------------------------

    try:
        db.commit()

        db.refresh(renewal)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Policy renewal failed",
        )

    return renewal