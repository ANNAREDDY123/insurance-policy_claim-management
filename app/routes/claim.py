from datetime import date

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.claim import Claim
from app.models.customer import Customer
from app.models.policy import Policy
from app.models.user import User
from app.schemas.claim import (
    CLAIM_STATUSES,
    ClaimCreate,
    ClaimResponse,
    ClaimUpdate,
)
from app.services.claim_service import ClaimService
from app.services.notification_tasks import (
    send_notification_background,
)
from app.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/claims",
    tags=["Claims"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_claim_or_404(
    db: Session,
    claim_id: int,
):
    claim = ClaimService.get_claim(
        db=db,
        claim_id=claim_id,
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )

    return claim


def get_policy_or_404(
    db: Session,
    policy_id: int,
):
    policy = ClaimService.get_policy(
        db=db,
        policy_id=policy_id,
    )

    if not policy:
        raise HTTPException(
            status_code=404,
            detail="Policy not found",
        )

    return policy


def get_customer_or_404(
    db: Session,
    customer_id: int,
):
    customer = ClaimService.get_customer(
        db=db,
        customer_id=customer_id,
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


def validate_claim_status(
    status: str,
):
    if status not in CLAIM_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid claim status",
        )


def validate_incident_date(
    policy: Policy,
    incident_date: date,
):
    if incident_date < policy.start_date:
        raise HTTPException(
            status_code=400,
            detail=(
                "Incident date must fall "
                "within policy coverage"
            ),
        )

    if incident_date > policy.end_date:
        raise HTTPException(
            status_code=400,
            detail=(
                "Incident date must fall "
                "within policy coverage"
            ),
        )


def check_claim_number(
    db: Session,
    claim_number: str,
):
    existing = ClaimService.get_claim_by_number(
        db=db,
        claim_number=claim_number,
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Claim number already exists",
        )


def check_duplicate_claim(
    db: Session,
    policy_id: int,
    incident_date: date,
    exclude_claim_id: int | None = None,
):
    existing = (
        ClaimService
        .get_claim_by_policy_and_incident_date_excluding_id(
            db=db,
            policy_id=policy_id,
            incident_date=incident_date,
            claim_id=exclude_claim_id,
        )
        if exclude_claim_id is not None
        else ClaimService.get_claim_by_policy_and_incident_date(
            db=db,
            policy_id=policy_id,
            incident_date=incident_date,
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                "A claim already exists "
                "for this incident date"
            ),
        )


# ============================================================
# CREATE CLAIM
# ============================================================

@router.post(
    "",
    response_model=ClaimResponse,
)
def create_claim(
    claim_data: ClaimCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Customer",
        )
    ),
):
    validate_claim_status(
        claim_data.status
    )

    policy = get_policy_or_404(
        db=db,
        policy_id=claim_data.policy_id,
    )

    customer = get_customer_or_404(
        db=db,
        customer_id=claim_data.customer_id,
    )

    if policy.policy_status != "Active":
        raise HTTPException(
            status_code=400,
            detail=(
                "Claim can only be created "
                "for an active policy"
            ),
        )

    if policy.customer_id != customer.id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Customer does not belong "
                "to this policy"
            ),
        )

    validate_incident_date(
        policy=policy,
        incident_date=claim_data.incident_date,
    )

    if claim_data.claim_amount > policy.coverage_amount:
        raise HTTPException(
            status_code=400,
            detail=(
                "Claim amount cannot exceed "
                "policy coverage amount"
            ),
        )

    check_claim_number(
        db=db,
        claim_number=claim_data.claim_number,
    )

    check_duplicate_claim(
        db=db,
        policy_id=claim_data.policy_id,
        incident_date=claim_data.incident_date,
    )

    claim = Claim(
        claim_number=claim_data.claim_number,
        policy_id=claim_data.policy_id,
        customer_id=claim_data.customer_id,
        claim_type=claim_data.claim_type,
        incident_date=claim_data.incident_date,
        claim_amount=claim_data.claim_amount,
        description=claim_data.description,
        status=claim_data.status,
    )

    try:
        claim = ClaimService.create_claim(
            db=db,
            claim=claim,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Claim number already exists",
        )

    # LEVEL 14 - CLAIM SUBMISSION NOTIFICATION
    send_notification_background(
        background_tasks=background_tasks,
        db=db,
        user_id=current_user.id,
        notification_type="CLAIM_SUBMISSION",
        title="Claim Submitted",
        message=(
            f"Your claim {claim.claim_number} "
            f"has been submitted successfully."
        ),
    )

    return claim


# ============================================================
# GET CLAIMS
# LEVEL 12 - SEARCH, FILTERING & PAGINATION
# ============================================================

@router.get(
    "",
    response_model=list[ClaimResponse],
)
def get_claims(
    status: str | None = None,
    claim_status: str | None = None,
    claim_type: str | None = None,
    customer_id: int | None = None,
    policy_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    amount_min: float | None = Query(
        default=None,
        ge=0,
    ),
    amount_max: float | None = Query(
        default=None,
        ge=0,
    ),
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
    current_user: User = Depends(
        get_current_user
    ),
):
    if (
        status is not None
        and claim_status is not None
        and status != claim_status
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "status and claim_status must match "
                "when both are provided"
            ),
        )

    selected_status = (
        claim_status
        if claim_status is not None
        else status
    )

    if selected_status is not None:
        validate_claim_status(
            selected_status
        )

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

    if (
        amount_min is not None
        and amount_max is not None
        and amount_min > amount_max
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "amount_min cannot be greater "
                "than amount_max"
            ),
        )

    allowed_sort_fields = {
        "id",
        "claim_number",
        "claim_type",
        "incident_date",
        "claim_amount",
        "status",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort_by. Allowed values: "
                + ", ".join(
                    allowed_sort_fields
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

    return ClaimService.get_claims(
        db=db,
        status=selected_status,
        claim_type=claim_type,
        customer_id=customer_id,
        policy_id=policy_id,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ============================================================
# GET SINGLE CLAIM
# ============================================================

@router.get(
    "/{claim_id}",
    response_model=ClaimResponse,
)
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )


# ============================================================
# UPDATE CLAIM
# ============================================================

@router.put(
    "/{claim_id}",
    response_model=ClaimResponse,
)
def update_claim(
    claim_id: int,
    claim_data: ClaimUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Customer",
        )
    ),
):
    claim = get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    policy = get_policy_or_404(
        db=db,
        policy_id=claim.policy_id,
    )

    if claim_data.claim_type is not None:
        claim.claim_type = (
            claim_data.claim_type
        )

    if claim_data.incident_date is not None:
        validate_incident_date(
            policy=policy,
            incident_date=(
                claim_data.incident_date
            ),
        )

        check_duplicate_claim(
            db=db,
            policy_id=claim.policy_id,
            incident_date=(
                claim_data.incident_date
            ),
            exclude_claim_id=claim.id,
        )

        claim.incident_date = (
            claim_data.incident_date
        )

    if claim_data.claim_amount is not None:
        if (
            claim_data.claim_amount
            > policy.coverage_amount
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Claim amount cannot exceed "
                    "policy coverage amount"
                ),
            )

        claim.claim_amount = (
            claim_data.claim_amount
        )

    if claim_data.description is not None:
        claim.description = (
            claim_data.description
        )

    if claim_data.status is not None:
        validate_claim_status(
            claim_data.status
        )

        claim.status = (
            claim_data.status
        )

    try:
        claim = ClaimService.update_claim(
            db=db,
            claim=claim,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Unable to update claim",
        )

    return claim


# ============================================================
# SUBMIT CLAIM
# ============================================================

@router.post(
    "/{claim_id}/submit",
    response_model=ClaimResponse,
)
def submit_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Customer",
        )
    ),
):
    claim = get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    if claim.status not in {
        "Submitted",
        "Documents Required",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Claim cannot be submitted "
                "from its current status"
            ),
        )

    claim.status = "Under Review"

    try:
        claim = ClaimService.update_claim(
            db=db,
            claim=claim,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to submit claim",
        )

    return claim


# ============================================================
# APPROVE CLAIM
# ============================================================

@router.post(
    "/{claim_id}/approve",
    response_model=ClaimResponse,
)
def approve_claim(
    claim_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
        )
    ),
):
    claim = get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    if claim.status != "Under Review":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only claims under review "
                "can be approved"
            ),
        )

    claim.status = "Approved"

    try:
        claim = ClaimService.update_claim(
            db=db,
            claim=claim,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to approve claim",
        )

    # LEVEL 14 - CLAIM APPROVAL NOTIFICATION
    send_notification_background(
        background_tasks=background_tasks,
        db=db,
        user_id=current_user.id,
        notification_type="CLAIM_APPROVED",
        title="Claim Approved",
        message=(
            f"Your claim {claim.claim_number} "
            f"has been approved."
        ),
    )

    return claim


# ============================================================
# REJECT CLAIM
# ============================================================

@router.post(
    "/{claim_id}/reject",
    response_model=ClaimResponse,
)
def reject_claim(
    claim_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
        )
    ),
):
    claim = get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    if claim.status != "Under Review":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only claims under review "
                "can be rejected"
            ),
        )

    claim.status = "Rejected"

    try:
        claim = ClaimService.update_claim(
            db=db,
            claim=claim,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to reject claim",
        )

    # LEVEL 14 - CLAIM REJECTION NOTIFICATION
    send_notification_background(
        background_tasks=background_tasks,
        db=db,
        user_id=current_user.id,
        notification_type="CLAIM_REJECTED",
        title="Claim Rejected",
        message=(
            f"Your claim {claim.claim_number} "
            f"has been rejected."
        ),
    )

    return claim