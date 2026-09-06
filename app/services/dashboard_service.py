from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import (
    DashboardRepository,
)


class DashboardService:

    # ============================================================
    # DASHBOARD
    # ============================================================

    @staticmethod
    def get_dashboard(
        db: Session,
    ):
        return {
            "total_customers": (
                DashboardRepository
                .get_total_customers(db)
            ),
            "active_policies": (
                DashboardRepository
                .get_active_policies(db)
            ),
            "expired_policies": (
                DashboardRepository
                .get_expired_policies(db)
            ),
            "total_premium_collected": (
                DashboardRepository
                .get_total_premium_collected(db)
            ),
            "pending_premium": (
                DashboardRepository
                .get_pending_premium(db)
            ),
            "total_claims": (
                DashboardRepository
                .get_total_claims(db)
            ),
            "approved_claims": (
                DashboardRepository
                .get_approved_claims(db)
            ),
            "rejected_claims": (
                DashboardRepository
                .get_rejected_claims(db)
            ),
            "pending_claims": (
                DashboardRepository
                .get_pending_claims(db)
            ),
            "total_settlement_amount": (
                DashboardRepository
                .get_total_settlement_amount(db)
            ),
        }

    # ============================================================
    # POLICY PREMIUM REPORT
    # ============================================================

    @staticmethod
    def get_policy_premium_report(
        db: Session,
    ):
        rows = (
            DashboardRepository
            .get_policy_premium_report(db)
        )

        return [
            {
                "policy_id": row.policy_id,
                "policy_number": row.policy_number,
                "customer_id": row.customer_id,
                "premium_amount": float(
                    row.premium_amount
                ),
                "total_paid": float(
                    row.total_paid or 0
                ),
            }
            for row in rows
        ]

    # ============================================================
    # CUSTOMER POLICY HISTORY
    # ============================================================

    @staticmethod
    def get_customer_policy_history(
        db: Session,
    ):
        rows = (
            DashboardRepository
            .get_customer_policy_history(db)
        )

        return [
            {
                "customer_id": row.customer_id,
                "customer_name": row.customer_name,
                "policy_id": row.policy_id,
                "policy_number": row.policy_number,
                "plan_id": row.plan_id,
                "start_date": (
                    row.start_date.isoformat()
                ),
                "end_date": (
                    row.end_date.isoformat()
                ),
                "policy_status": (
                    row.policy_status
                ),
                "premium_amount": float(
                    row.premium_amount
                ),
            }
            for row in rows
        ]

    # ============================================================
    # CLAIM SETTLEMENT REPORT
    # ============================================================

    @staticmethod
    def get_claim_settlement_report(
        db: Session,
    ):
        rows = (
            DashboardRepository
            .get_claim_settlement_report(db)
        )

        return [
            {
                "claim_id": row.claim_id,
                "claim_number": row.claim_number,
                "customer_id": row.customer_id,
                "claim_amount": float(
                    row.claim_amount
                ),
                "claim_status": row.claim_status,
                "settlement_amount": (
                    float(
                        row.settlement_amount
                    )
                    if row.settlement_amount
                    is not None
                    else None
                ),
                "settlement_status": (
                    row.settlement_status
                ),
            }
            for row in rows
        ]

    # ============================================================
    # AGENT PERFORMANCE REPORT
    # ============================================================

    @staticmethod
    def get_agent_performance_report(
        db: Session,
    ):
        rows = (
            DashboardRepository
            .get_agent_performance_report(db)
        )

        return [
            {
                "agent_id": row.agent_id,
                "agent_name": row.agent_name,
                "total_policies": int(
                    row.total_policies or 0
                ),
                "active_policies": int(
                    row.active_policies or 0
                ),
                "total_premium": float(
                    row.total_premium or 0
                ),
            }
            for row in rows
        ]

    # ============================================================
    # MONTHLY PREMIUM REPORT
    # ============================================================

    @staticmethod
    def get_monthly_premium_report(
        db: Session,
    ):
        rows = (
            DashboardRepository
            .get_monthly_premium_report(db)
        )

        return [
            {
                "month": row.month,
                "total_premium_collected": float(
                    row.total_premium_collected
                    or 0
                ),
            }
            for row in rows
        ]

    # ============================================================
    # MONTHLY CLAIM REPORT
    # ============================================================

    @staticmethod
    def get_monthly_claim_report(
        db: Session,
    ):
        rows = (
            DashboardRepository
            .get_monthly_claim_report(db)
        )

        return [
            {
                "month": row.month,
                "total_claims": int(
                    row.total_claims or 0
                ),
                "total_claim_amount": float(
                    row.total_claim_amount
                    or 0
                ),
            }
            for row in rows
        ]