from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import (
    AgentPerformanceReport,
    ClaimSettlementReport,
    CustomerPolicyHistory,
    DashboardResponse,
    MonthlyClaimReport,
    MonthlyPremiumReport,
    PolicyPremiumReport,
)
from app.services.dashboard_service import (
    DashboardService,
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    tags=["Dashboard & Reports"],
)


# ============================================================
# DASHBOARD
# ============================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return DashboardService.get_dashboard(
        db=db,
    )


# ============================================================
# POLICY-WISE PREMIUM REPORT
# ============================================================

@router.get(
    "/reports/policy-premium",
    response_model=list[PolicyPremiumReport],
)
def policy_premium_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        DashboardService
        .get_policy_premium_report(db)
    )


# ============================================================
# CUSTOMER POLICY HISTORY REPORT
# ============================================================

@router.get(
    "/reports/customer-policy-history",
    response_model=list[CustomerPolicyHistory],
)
def customer_policy_history_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        DashboardService
        .get_customer_policy_history(db)
    )


# ============================================================
# CLAIM SETTLEMENT REPORT
# ============================================================

@router.get(
    "/reports/claim-settlement",
    response_model=list[ClaimSettlementReport],
)
def claim_settlement_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        DashboardService
        .get_claim_settlement_report(db)
    )


# ============================================================
# AGENT PERFORMANCE REPORT
# ============================================================

@router.get(
    "/reports/agent-performance",
    response_model=list[AgentPerformanceReport],
)
def agent_performance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        DashboardService
        .get_agent_performance_report(db)
    )


# ============================================================
# MONTHLY PREMIUM COLLECTION REPORT
# ============================================================

@router.get(
    "/reports/monthly-premium",
    response_model=list[MonthlyPremiumReport],
)
def monthly_premium_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        DashboardService
        .get_monthly_premium_report(db)
    )


# ============================================================
# MONTHLY CLAIM STATISTICS REPORT
# ============================================================

@router.get(
    "/reports/monthly-claims",
    response_model=list[MonthlyClaimReport],
)
def monthly_claim_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return (
        DashboardService
        .get_monthly_claim_report(db)
    )