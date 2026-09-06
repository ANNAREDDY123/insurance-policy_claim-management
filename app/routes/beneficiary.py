from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.beneficiary import Beneficiary
from app.models.policy import Policy
from app.models.user import User
from app.schemas.beneficiary import (
    BeneficiaryCreate,
    BeneficiaryResponse,
    BeneficiaryUpdate,
)
from app.utils.dependencies import get_current_user, require_roles


# Routes under /policies
router = APIRouter(
    prefix="/policies",
    tags=["Beneficiaries"],
)


# Routes under /beneficiaries
beneficiary_router = APIRouter(
    prefix="/beneficiaries",
    tags=["Beneficiaries"],
)


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


def get_beneficiary_or_404(
    db: Session,
    beneficiary_id: int,
):
    beneficiary = (
        db.query(Beneficiary)
        .filter(Beneficiary.id == beneficiary_id)
        .first()
    )

    if not beneficiary:
        raise HTTPException(
            status_code=404,
            detail="Beneficiary not found",
        )

    return beneficiary


def validate_total_percentage(
    db: Session,
    policy_id: int,
    new_percentage: float,
    exclude_id: int | None = None,
):
    query = db.query(Beneficiary).filter(
        Beneficiary.policy_id == policy_id
    )

    if exclude_id is not None:
        query = query.filter(
            Beneficiary.id != exclude_id
        )

    existing_total = sum(
        beneficiary.percentage
        for beneficiary in query.all()
    )

    new_total = existing_total + new_percentage

    if new_total > 100:
        raise HTTPException(
            status_code=400,
            detail=(
                "Beneficiary percentages "
                "cannot exceed 100%"
            ),
        )


def validate_final_percentage(
    db: Session,
    policy_id: int,
):
    total = sum(
        beneficiary.percentage
        for beneficiary in db.query(
            Beneficiary
        )
        .filter(
            Beneficiary.policy_id == policy_id
        )
        .all()
    )

    if round(total, 2) != 100:
        raise HTTPException(
            status_code=400,
            detail=(
                "Beneficiary percentages must "
                "total exactly 100%"
            ),
        )


# =========================================================
# ADD BENEFICIARY
# POST /policies/{policy_id}/beneficiaries
# =========================================================

@router.post(
    "/{policy_id}/beneficiaries",
    response_model=BeneficiaryResponse,
)
def create_beneficiary(
    policy_id: int,
    beneficiary_data: BeneficiaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
            "Customer",
        )
    ),
):
    get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )

    duplicate = (
        db.query(Beneficiary)
        .filter(
            Beneficiary.policy_id == policy_id,
            Beneficiary.identification_number
            == beneficiary_data.identification_number,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=(
                "Beneficiary already exists "
                "for this policy"
            ),
        )

    validate_total_percentage(
        db=db,
        policy_id=policy_id,
        new_percentage=beneficiary_data.percentage,
    )

    beneficiary = Beneficiary(
        policy_id=policy_id,
        name=beneficiary_data.name,
        relationship=beneficiary_data.relationship,
        percentage=beneficiary_data.percentage,
        phone=beneficiary_data.phone,
        identification_number=(
            beneficiary_data.identification_number
        ),
    )

    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)

    return beneficiary


# =========================================================
# GET BENEFICIARIES
# GET /policies/{policy_id}/beneficiaries
# =========================================================

@router.get(
    "/{policy_id}/beneficiaries",
    response_model=list[BeneficiaryResponse],
)
def get_beneficiaries(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_policy_or_404(
        db=db,
        policy_id=policy_id,
    )

    return (
        db.query(Beneficiary)
        .filter(
            Beneficiary.policy_id == policy_id
        )
        .order_by(Beneficiary.id)
        .all()
    )


# =========================================================
# UPDATE BENEFICIARY
# PUT /beneficiaries/{beneficiary_id}
# =========================================================

@beneficiary_router.put(
    "/{beneficiary_id}",
    response_model=BeneficiaryResponse,
)
def update_beneficiary(
    beneficiary_id: int,
    beneficiary_data: BeneficiaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
            "Customer",
        )
    ),
):
    beneficiary = get_beneficiary_or_404(
        db=db,
        beneficiary_id=beneficiary_id,
    )

    # Check duplicate identification number
    if (
        beneficiary_data.identification_number
        is not None
    ):
        duplicate = (
            db.query(Beneficiary)
            .filter(
                Beneficiary.policy_id
                == beneficiary.policy_id,
                Beneficiary.identification_number
                == beneficiary_data.identification_number,
                Beneficiary.id != beneficiary.id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Beneficiary already exists "
                    "for this policy"
                ),
            )

        beneficiary.identification_number = (
            beneficiary_data.identification_number
        )

    # Validate percentage
    if beneficiary_data.percentage is not None:
        validate_total_percentage(
            db=db,
            policy_id=beneficiary.policy_id,
            new_percentage=beneficiary_data.percentage,
            exclude_id=beneficiary.id,
        )

        beneficiary.percentage = (
            beneficiary_data.percentage
        )

    if beneficiary_data.name is not None:
        beneficiary.name = (
            beneficiary_data.name
        )

    if beneficiary_data.relationship is not None:
        beneficiary.relationship = (
            beneficiary_data.relationship
        )

    if beneficiary_data.phone is not None:
        beneficiary.phone = (
            beneficiary_data.phone
        )

    db.commit()
    db.refresh(beneficiary)

    return beneficiary


# =========================================================
# DELETE BENEFICIARY
# DELETE /beneficiaries/{beneficiary_id}
# =========================================================

@beneficiary_router.delete(
    "/{beneficiary_id}",
)
def delete_beneficiary(
    beneficiary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
            "Customer",
        )
    ),
):
    beneficiary = get_beneficiary_or_404(
        db=db,
        beneficiary_id=beneficiary_id,
    )

    db.delete(beneficiary)
    db.commit()

    return {
        "message": "Beneficiary deleted successfully"
    }