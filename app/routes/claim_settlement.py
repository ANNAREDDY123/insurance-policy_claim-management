from datetime import datetime

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.claim_settlement import ClaimSettlement
from app.models.user import User
from app.schemas.claim_settlement import (
    SETTLEMENT_STATUSES,
    ClaimSettlementCreate,
    ClaimSettlementResponse,
)
from app.services.claim_service import ClaimService
from app.services.claim_settlement_service import (
    ClaimSettlementService,
)
from app.services.notification_tasks import (
    send_notification_background,
)
from app.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    tags=["Claim Settlement"],
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


def get_settlement_or_404(
    db: Session,
    settlement_id: int,
):
    settlement = (
        ClaimSettlementService.get_settlement(
            db=db,
            settlement_id=settlement_id,
        )
    )

    if not settlement:
        raise HTTPException(
            status_code=404,
            detail="Settlement not found",
        )

    return settlement


# ============================================================
# SETTLE CLAIM
# ============================================================

@router.post(
    "/claims/{claim_id}/settle",
    response_model=ClaimSettlementResponse,
)
def settle_claim(
    claim_id: int,
    settlement_data: ClaimSettlementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Finance Officer",
        )
    ),
):
    claim = get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    # --------------------------------------------------------
    # Make sure claim ID in body matches URL
    # --------------------------------------------------------

    if settlement_data.claim_id != claim_id:
        raise HTTPException(
            status_code=400,
            detail="Claim ID mismatch",
        )

    # --------------------------------------------------------
    # Check for existing settlement
    # --------------------------------------------------------

    existing_settlement = (
        ClaimSettlementService
        .get_settlement_by_claim_id(
            db=db,
            claim_id=claim_id,
        )
    )

    if existing_settlement:
        raise HTTPException(
            status_code=409,
            detail="Claim has already been settled",
        )

    # --------------------------------------------------------
    # Only approved claims can be settled
    # --------------------------------------------------------

    if claim.status != "Approved":
        raise HTTPException(
            status_code=400,
            detail="Only approved claims can be settled",
        )

    # --------------------------------------------------------
    # Validate settlement status
    # --------------------------------------------------------

    if (
        settlement_data.settlement_status
        not in SETTLEMENT_STATUSES
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid settlement status",
        )

    # --------------------------------------------------------
    # Validate settlement amount
    # --------------------------------------------------------

    if (
        settlement_data.settlement_amount
        > claim.claim_amount
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Settlement amount cannot exceed "
                "approved claim amount"
            ),
        )

    # --------------------------------------------------------
    # Set settlement date
    # --------------------------------------------------------

    settled_at = None

    if (
        settlement_data.settlement_status
        == "Completed"
    ):
        settled_at = datetime.utcnow()

    # --------------------------------------------------------
    # Create settlement
    # --------------------------------------------------------

    settlement = ClaimSettlement(
        claim_id=claim_id,
        settled_by=current_user.id,
        settlement_amount=(
            settlement_data.settlement_amount
        ),
        settlement_status=(
            settlement_data.settlement_status
        ),
        payment_reference=(
            settlement_data.payment_reference
        ),
        remarks=settlement_data.remarks,
        settled_at=settled_at,
    )

    # --------------------------------------------------------
    # Completed settlement changes claim status
    # --------------------------------------------------------

    if (
        settlement_data.settlement_status
        == "Completed"
    ):
        claim.status = "Settled"

    # --------------------------------------------------------
    # Save using Service Layer
    # --------------------------------------------------------

    settlement = (
        ClaimSettlementService.create_settlement(
            db=db,
            settlement=settlement,
        )
    )

    # ========================================================
    # LEVEL 14 - CLAIM SETTLEMENT NOTIFICATION
    # ========================================================

    if (
        settlement_data.settlement_status
        == "Completed"
    ):
        send_notification_background(
            background_tasks=background_tasks,
            db=db,
            user_id=current_user.id,
            notification_type="CLAIM_SETTLEMENT",
            title="Claim Settlement Completed",
            message=(
                f"Claim {claim.claim_number} "
                f"has been settled successfully for "
                f"{settlement.settlement_amount}."
            ),
        )

    return settlement


# ============================================================
# GET ALL SETTLEMENTS
# ============================================================

@router.get(
    "/settlements",
    response_model=list[ClaimSettlementResponse],
)
def get_settlements(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        ClaimSettlementService.get_settlements(
            db=db,
        )
    )


# ============================================================
# GET SINGLE SETTLEMENT
# ============================================================

@router.get(
    "/settlements/{settlement_id}",
    response_model=ClaimSettlementResponse,
)
def get_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_settlement_or_404(
        db=db,
        settlement_id=settlement_id,
    )