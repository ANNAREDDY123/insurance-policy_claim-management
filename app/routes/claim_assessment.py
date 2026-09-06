from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.claim import Claim
from app.models.claim_assessment import ClaimAssessment
from app.models.user import User
from app.schemas.claim_assessment import (
    ClaimAssessmentCreate,
    ClaimAssessmentResponse,
    ClaimAssessmentUpdate,
)
from app.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/claims",
    tags=["Claim Assessment"],
)


def get_claim_or_404(
    db: Session,
    claim_id: int,
):
    claim = (
        db.query(Claim)
        .filter(Claim.id == claim_id)
        .first()
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )

    return claim


def get_assessment_or_404(
    db: Session,
    assessment_id: int,
):
    assessment = (
        db.query(ClaimAssessment)
        .filter(
            ClaimAssessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Claim assessment not found",
        )

    return assessment


@router.post(
    "/{claim_id}/assessments",
    response_model=ClaimAssessmentResponse,
)
def create_assessment(
    claim_id: int,
    assessment_data: ClaimAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    if assessment_data.claim_id != claim_id:
        raise HTTPException(
            status_code=400,
            detail="Claim ID mismatch",
        )

    existing_assessment = (
        db.query(ClaimAssessment)
        .filter(
            ClaimAssessment.claim_id == claim_id
        )
        .first()
    )

    if existing_assessment:
        raise HTTPException(
            status_code=409,
            detail="Assessment already exists for this claim",
        )

    assessment = ClaimAssessment(
        claim_id=claim_id,
        assessor_id=current_user.id,
        assessment_status=(
            assessment_data.assessment_status
        ),
        approved_amount=(
            assessment_data.approved_amount
        ),
        remarks=assessment_data.remarks,
        assessed_at=datetime.utcnow(),
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment


@router.get(
    "/{claim_id}/assessments",
    response_model=list[ClaimAssessmentResponse],
)
def get_claim_assessments(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    return (
        db.query(ClaimAssessment)
        .filter(
            ClaimAssessment.claim_id == claim_id
        )
        .order_by(ClaimAssessment.id)
        .all()
    )


@router.get(
    "/assessments/{assessment_id}",
    response_model=ClaimAssessmentResponse,
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_assessment_or_404(
        db=db,
        assessment_id=assessment_id,
    )


@router.put(
    "/assessments/{assessment_id}",
    response_model=ClaimAssessmentResponse,
)
def update_assessment(
    assessment_id: int,
    assessment_data: ClaimAssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Insurance Agent",
        )
    ),
):
    assessment = get_assessment_or_404(
        db=db,
        assessment_id=assessment_id,
    )

    if assessment_data.assessment_status is not None:
        assessment.assessment_status = (
            assessment_data.assessment_status
        )

    if assessment_data.approved_amount is not None:
        assessment.approved_amount = (
            assessment_data.approved_amount
        )

    if assessment_data.remarks is not None:
        assessment.remarks = (
            assessment_data.remarks
        )

    assessment.assessed_at = datetime.utcnow()

    db.commit()
    db.refresh(assessment)

    return assessment


@router.delete(
    "/assessments/{assessment_id}",
)
def delete_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
        )
    ),
):
    assessment = get_assessment_or_404(
        db=db,
        assessment_id=assessment_id,
    )

    db.delete(assessment)
    db.commit()

    return {
        "message": "Claim assessment deleted successfully"
    }