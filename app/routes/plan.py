from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.plan import Plan
from app.models.user import User
from app.schemas.plan import (
    PLAN_STATUSES,
    PLAN_TYPES,
    PlanCreate,
    PlanResponse,
    PlanUpdate,
)
from app.services.plan_service import PlanService
from app.utils.dependencies import get_current_user, require_roles


router = APIRouter(
    prefix="/plans",
    tags=["Insurance Plans"],
)


def validate_plan_data(
    plan_type: str,
    status: str,
    coverage_amount: float,
    premium_amount: float,
    eligibility_age_min: int,
    eligibility_age_max: int,
):
    if plan_type not in PLAN_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid plan type",
        )

    if status not in PLAN_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid plan status",
        )

    if coverage_amount <= premium_amount:
        raise HTTPException(
            status_code=400,
            detail="Coverage amount must be greater than premium amount",
        )

    if premium_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Premium amount must be greater than 0",
        )

    if eligibility_age_min > eligibility_age_max:
        raise HTTPException(
            status_code=400,
            detail="Minimum eligibility age cannot exceed maximum eligibility age",
        )


def get_plan_or_404(
    db: Session,
    plan_id: int,
):
    plan = PlanService.get_plan(
        db=db,
        plan_id=plan_id,
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Insurance plan not found",
        )

    return plan


@router.post(
    "",
    response_model=PlanResponse,
)
def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    validate_plan_data(
        plan_type=plan_data.plan_type,
        status=plan_data.status,
        coverage_amount=plan_data.coverage_amount,
        premium_amount=plan_data.premium_amount,
        eligibility_age_min=plan_data.eligibility_age_min,
        eligibility_age_max=plan_data.eligibility_age_max,
    )

    existing_plan = PlanService.get_plan_by_name(
        db=db,
        plan_name=plan_data.plan_name,
    )

    if existing_plan:
        raise HTTPException(
            status_code=409,
            detail="Insurance plan already exists",
        )

    plan = Plan(
        plan_name=plan_data.plan_name,
        plan_type=plan_data.plan_type,
        description=plan_data.description,
        coverage_amount=plan_data.coverage_amount,
        premium_amount=plan_data.premium_amount,
        duration_years=plan_data.duration_years,
        eligibility_age_min=plan_data.eligibility_age_min,
        eligibility_age_max=plan_data.eligibility_age_max,
        status=plan_data.status,
    )

    try:
        plan = PlanService.create_plan(
            db=db,
            plan=plan,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Insurance plan already exists",
        )

    return plan


@router.get(
    "",
    response_model=list[PlanResponse],
)
def get_plans(
    plan_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if plan_type is not None:
        if plan_type not in PLAN_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid plan type",
            )

    if status is not None:
        if status not in PLAN_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Invalid plan status",
            )

    return PlanService.get_plans(
        db=db,
        plan_type=plan_type,
        status=status,
    )


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_plan_or_404(
        db=db,
        plan_id=plan_id,
    )


@router.put(
    "/{plan_id}",
    response_model=PlanResponse,
)
def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    plan = get_plan_or_404(
        db=db,
        plan_id=plan_id,
    )

    new_plan_type = (
        plan_data.plan_type
        if plan_data.plan_type is not None
        else plan.plan_type
    )

    new_status = (
        plan_data.status
        if plan_data.status is not None
        else plan.status
    )

    new_coverage = (
        plan_data.coverage_amount
        if plan_data.coverage_amount is not None
        else plan.coverage_amount
    )

    new_premium = (
        plan_data.premium_amount
        if plan_data.premium_amount is not None
        else plan.premium_amount
    )

    new_min_age = (
        plan_data.eligibility_age_min
        if plan_data.eligibility_age_min is not None
        else plan.eligibility_age_min
    )

    new_max_age = (
        plan_data.eligibility_age_max
        if plan_data.eligibility_age_max is not None
        else plan.eligibility_age_max
    )

    validate_plan_data(
        plan_type=new_plan_type,
        status=new_status,
        coverage_amount=new_coverage,
        premium_amount=new_premium,
        eligibility_age_min=new_min_age,
        eligibility_age_max=new_max_age,
    )

    if plan_data.plan_name is not None:
        existing_plan = (
            PlanService.get_plan_by_name_excluding_id(
                db=db,
                plan_name=plan_data.plan_name,
                plan_id=plan.id,
            )
        )

        if existing_plan:
            raise HTTPException(
                status_code=409,
                detail="Insurance plan already exists",
            )

        plan.plan_name = plan_data.plan_name

    if plan_data.plan_type is not None:
        plan.plan_type = plan_data.plan_type

    if plan_data.description is not None:
        plan.description = plan_data.description

    if plan_data.coverage_amount is not None:
        plan.coverage_amount = (
            plan_data.coverage_amount
        )

    if plan_data.premium_amount is not None:
        plan.premium_amount = (
            plan_data.premium_amount
        )

    if plan_data.duration_years is not None:
        plan.duration_years = (
            plan_data.duration_years
        )

    if plan_data.eligibility_age_min is not None:
        plan.eligibility_age_min = (
            plan_data.eligibility_age_min
        )

    if plan_data.eligibility_age_max is not None:
        plan.eligibility_age_max = (
            plan_data.eligibility_age_max
        )

    if plan_data.status is not None:
        plan.status = plan_data.status

    try:
        plan = PlanService.update_plan(
            db=db,
            plan=plan,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Insurance plan already exists",
        )

    return plan


@router.delete(
    "/{plan_id}",
)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
        )
    ),
):
    plan = get_plan_or_404(
        db=db,
        plan_id=plan_id,
    )

    PlanService.delete_plan(
        db=db,
        plan=plan,
    )

    return {
        "message": "Insurance plan deleted successfully"
    }