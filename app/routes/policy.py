from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.plan import Plan
from app.models.policy import Policy
from app.models.user import User
from app.schemas.policy import (
    POLICY_STATUSES,
    PolicyCreate,
    PolicyResponse,
    PolicyUpdate,
)
from app.services.policy_service import PolicyService
from app.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_age(
    date_of_birth: date,
) -> int:
    today = date.today()

    return (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (
                date_of_birth.month,
                date_of_birth.day,
            )
        )
    )


def get_customer_or_404(
    db: Session,
    customer_id: int,
):
    customer = PolicyService.get_customer(
        db=db,
        customer_id=customer_id,
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


def get_plan_or_404(
    db: Session,
    plan_id: int,
):
    plan = PolicyService.get_plan(
        db=db,
        plan_id=plan_id,
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Insurance plan not found",
        )

    return plan


def get_policy_or_404(
    db: Session,
    policy_id: int,
):
    policy = PolicyService.get_policy(
        db=db,
        policy_id=policy_id,
    )

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Policy not found",
        )

    return policy


def validate_policy_dates(
    start_date: date,
    end_date: date,
):
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date",
        )


def validate_policy_status(
    status: str,
):
    if status not in POLICY_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid policy status",
        )


def validate_customer_eligibility(
    customer: Customer,
    plan: Plan,
):
    age = calculate_age(
        customer.date_of_birth
    )

    if age < plan.eligibility_age_min:
        raise HTTPException(
            status_code=400,
            detail=(
                "Customer does not meet "
                "minimum age eligibility"
            ),
        )

    if age > plan.eligibility_age_max:
        raise HTTPException(
            status_code=400,
            detail=(
                "Customer exceeds "
                "maximum age eligibility"
            ),
        )


def check_policy_number(
    db: Session,
    policy_number: str,
):
    existing = PolicyService.get_policy_by_number(
        db=db,
        policy_number=policy_number,
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Policy number already exists",
        )


def check_overlapping_policy(
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
            Policy.start_date <= end_date,
            Policy.end_date >= start_date,
        )
    )

    if exclude_policy_id is not None:
        query = query.filter(
            Policy.id != exclude_policy_id
        )

    existing = query.first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                "Customer already has an active "
                "overlapping policy for this plan"
            ),
        )


# ============================================================
# CREATE POLICY
# ============================================================

@router.post(
    "",
    response_model=PolicyResponse,
)
def create_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    validate_policy_dates(
        start_date=policy_data.start_date,
        end_date=policy_data.end_date,
    )

    validate_policy_status(
        policy_data.policy_status
    )

    if (
        policy_data.coverage_amount
        <= policy_data.premium_amount
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Coverage amount must be greater than "
                "premium amount"
            ),
        )

    customer = get_customer_or_404(
        db=db,
        customer_id=policy_data.customer_id,
    )

    plan = get_plan_or_404(
        db=db,
        plan_id=policy_data.plan_id,
    )

    if plan.status != "Active":
        raise HTTPException(
            status_code=400,
            detail="Inactive plans cannot be purchased",
        )

    validate_customer_eligibility(
        customer=customer,
        plan=plan,
    )

    agent = PolicyService.get_user(
        db=db,
        user_id=policy_data.agent_id,
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Insurance agent not found",
        )

    if agent.role != "Insurance Agent":
        raise HTTPException(
            status_code=400,
            detail=(
                "Assigned user must be an "
                "Insurance Agent"
            ),
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=400,
            detail=(
                "Insurance agent account is inactive"
            ),
        )

    check_policy_number(
        db=db,
        policy_number=policy_data.policy_number,
    )

    if policy_data.policy_status == "Active":
        check_overlapping_policy(
            db=db,
            customer_id=policy_data.customer_id,
            plan_id=policy_data.plan_id,
            start_date=policy_data.start_date,
            end_date=policy_data.end_date,
        )

    policy = Policy(
        policy_number=policy_data.policy_number,
        customer_id=policy_data.customer_id,
        plan_id=policy_data.plan_id,
        agent_id=policy_data.agent_id,
        start_date=policy_data.start_date,
        end_date=policy_data.end_date,
        coverage_amount=policy_data.coverage_amount,
        premium_amount=policy_data.premium_amount,
        policy_status=policy_data.policy_status,
    )

    try:
        policy = PolicyService.create_policy(
            db=db,
            policy=policy,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Policy number already exists",
        )

    return policy


# ============================================================
# GET POLICIES
# SEARCH, FILTERING, PAGINATION AND SORTING
# ============================================================

@router.get(
    "",
    response_model=list[PolicyResponse],
)
def get_policies(
    status: str | None = None,
    policy_status: str | None = None,
    customer_id: int | None = None,
    plan_id: int | None = None,
    agent_id: int | None = None,
    plan_type: str | None = None,
    customer: str | None = None,
    expiry_date: date | None = None,
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
        pattern="^(asc|desc)$",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    # --------------------------------------------------------
    # BACKWARD COMPATIBILITY
    # --------------------------------------------------------

    if (
        status is not None
        and policy_status is not None
        and status != policy_status
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "status and policy_status must match "
                "when both are provided"
            ),
        )

    selected_status = (
        policy_status
        if policy_status is not None
        else status
    )

    # --------------------------------------------------------
    # VALIDATE STATUS
    # --------------------------------------------------------

    if selected_status is not None:
        validate_policy_status(
            selected_status
        )

    # --------------------------------------------------------
    # VALIDATE SORTING
    # --------------------------------------------------------

    allowed_sort_fields = {
        "id",
        "policy_number",
        "start_date",
        "end_date",
        "coverage_amount",
        "premium_amount",
        "policy_status",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort field",
        )

    # --------------------------------------------------------
    # BUILD QUERY
    # --------------------------------------------------------

    query = (
        db.query(Policy)
        .join(
            Customer,
            Policy.customer_id == Customer.id,
        )
        .join(
            Plan,
            Policy.plan_id == Plan.id,
        )
    )

    # --------------------------------------------------------
    # FILTER BY POLICY STATUS
    # --------------------------------------------------------

    if selected_status is not None:
        query = query.filter(
            Policy.policy_status
            == selected_status
        )

    # --------------------------------------------------------
    # FILTER BY CUSTOMER ID
    # --------------------------------------------------------

    if customer_id is not None:
        query = query.filter(
            Policy.customer_id
            == customer_id
        )

    # --------------------------------------------------------
    # FILTER BY PLAN ID
    # --------------------------------------------------------

    if plan_id is not None:
        query = query.filter(
            Policy.plan_id
            == plan_id
        )

    # --------------------------------------------------------
    # FILTER BY AGENT ID
    # --------------------------------------------------------

    if agent_id is not None:
        query = query.filter(
            Policy.agent_id
            == agent_id
        )

    # --------------------------------------------------------
    # FILTER BY PLAN TYPE
    # --------------------------------------------------------

    if plan_type is not None:
        query = query.filter(
            Plan.plan_type == plan_type
        )

    # --------------------------------------------------------
    # SEARCH BY CUSTOMER
    # --------------------------------------------------------

    if customer is not None:
        query = query.filter(
            Customer.full_name.ilike(
                f"%{customer}%"
            )
        )

    # --------------------------------------------------------
    # FILTER BY EXPIRY DATE
    # --------------------------------------------------------

    if expiry_date is not None:
        query = query.filter(
            Policy.end_date <= expiry_date
        )

    # --------------------------------------------------------
    # SORTING
    # --------------------------------------------------------

    sort_column = getattr(
        Policy,
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

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    offset = (
        page - 1
    ) * limit

    return (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )


# ============================================================
# GET SINGLE POLICY
# ============================================================

@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )


# ============================================================
# UPDATE POLICY
# ============================================================

@router.put(
    "/{policy_id}",
    response_model=PolicyResponse,
)
def update_policy(
    policy_id: int,
    policy_data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    policy = get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )

    start_date = (
        policy_data.start_date
        if policy_data.start_date is not None
        else policy.start_date
    )

    end_date = (
        policy_data.end_date
        if policy_data.end_date is not None
        else policy.end_date
    )

    validate_policy_dates(
        start_date=start_date,
        end_date=end_date,
    )

    if policy_data.policy_status is not None:
        validate_policy_status(
            policy_data.policy_status
        )

        if (
            policy_data.policy_status == "Active"
            and policy.policy_status != "Active"
        ):
            check_overlapping_policy(
                db=db,
                customer_id=policy.customer_id,
                plan_id=policy.plan_id,
                start_date=start_date,
                end_date=end_date,
                exclude_policy_id=policy.id,
            )

        policy.policy_status = (
            policy_data.policy_status
        )

    if policy_data.coverage_amount is not None:
        policy.coverage_amount = (
            policy_data.coverage_amount
        )

    if policy_data.premium_amount is not None:
        policy.premium_amount = (
            policy_data.premium_amount
        )

    if (
        policy.coverage_amount
        <= policy.premium_amount
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Coverage amount must be greater than "
                "premium amount"
            ),
        )

    policy.start_date = start_date
    policy.end_date = end_date

    try:
        policy = PolicyService.update_policy(
            db=db,
            policy=policy,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update policy",
        )

    return policy


# ============================================================
# ACTIVATE POLICY
# ============================================================

@router.post(
    "/{policy_id}/activate",
    response_model=PolicyResponse,
)
def activate_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    policy = get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )

    if policy.policy_status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail=(
                "Cancelled policy cannot be activated"
            ),
        )

    if policy.policy_status == "Active":
        raise HTTPException(
            status_code=400,
            detail="Policy is already active",
        )

    if date.today() > policy.end_date:
        raise HTTPException(
            status_code=400,
            detail=(
                "Expired policy cannot be activated"
            ),
        )

    check_overlapping_policy(
        db=db,
        customer_id=policy.customer_id,
        plan_id=policy.plan_id,
        start_date=policy.start_date,
        end_date=policy.end_date,
        exclude_policy_id=policy.id,
    )

    policy.policy_status = "Active"

    try:
        policy = PolicyService.update_policy(
            db=db,
            policy=policy,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to activate policy",
        )

    return policy


# ============================================================
# CANCEL POLICY
# ============================================================

@router.post(
    "/{policy_id}/cancel",
    response_model=PolicyResponse,
)
def cancel_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    policy = get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )

    if policy.policy_status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="Policy is already cancelled",
        )

    policy.policy_status = "Cancelled"

    try:
        policy = PolicyService.update_policy(
            db=db,
            policy=policy,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to cancel policy",
        )

    return policy