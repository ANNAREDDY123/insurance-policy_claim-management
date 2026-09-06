from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.claim_settlement import ClaimSettlement
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.policy import Policy
from app.models.user import User


class DashboardRepository:

    # ============================================================
    # DASHBOARD STATISTICS
    # ============================================================

    @staticmethod
    def get_total_customers(db: Session) -> int:
        return (
            db.query(Customer)
            .filter(Customer.is_deleted == False)
            .count()
        )

    @staticmethod
    def get_active_policies(db: Session) -> int:
        return (
            db.query(Policy)
            .filter(
                Policy.policy_status == "Active"
            )
            .count()
        )

    @staticmethod
    def get_expired_policies(db: Session) -> int:
        return (
            db.query(Policy)
            .filter(
                Policy.policy_status == "Expired"
            )
            .count()
        )

    @staticmethod
    def get_total_premium_collected(
        db: Session,
    ) -> float:
        total = (
            db.query(
                func.coalesce(
                    func.sum(Payment.amount),
                    0,
                )
            )
            .filter(
                Payment.payment_status == "Success"
            )
            .scalar()
        )

        return float(total or 0)

    @staticmethod
    def get_pending_premium(
        db: Session,
    ) -> float:
        total = (
            db.query(
                func.coalesce(
                    func.sum(Payment.amount),
                    0,
                )
            )
            .filter(
                Payment.payment_status == "Pending"
            )
            .scalar()
        )

        return float(total or 0)

    @staticmethod
    def get_total_claims(db: Session) -> int:
        return (
            db.query(Claim)
            .count()
        )

    @staticmethod
    def get_approved_claims(
        db: Session,
    ) -> int:
        return (
            db.query(Claim)
            .filter(
                Claim.status == "Approved"
            )
            .count()
        )

    @staticmethod
    def get_rejected_claims(
        db: Session,
    ) -> int:
        return (
            db.query(Claim)
            .filter(
                Claim.status == "Rejected"
            )
            .count()
        )

    @staticmethod
    def get_pending_claims(
        db: Session,
    ) -> int:
        return (
            db.query(Claim)
            .filter(
                Claim.status.in_(
                    [
                        "Submitted",
                        "Under Review",
                        "Documents Required",
                    ]
                )
            )
            .count()
        )

    @staticmethod
    def get_total_settlement_amount(
        db: Session,
    ) -> float:
        total = (
            db.query(
                func.coalesce(
                    func.sum(
                        ClaimSettlement.settlement_amount
                    ),
                    0,
                )
            )
            .filter(
                ClaimSettlement.settlement_status
                == "Completed"
            )
            .scalar()
        )

        return float(total or 0)

    # ============================================================
    # REPORT QUERIES
    # ============================================================

    @staticmethod
    def get_policy_premium_report(
        db: Session,
    ):
        return (
            db.query(
                Policy.id.label("policy_id"),
                Policy.policy_number,
                Policy.customer_id,
                Policy.premium_amount,
                func.coalesce(
                    func.sum(Payment.amount),
                    0,
                ).label("total_paid"),
            )
            .outerjoin(
                Payment,
                (
                    (Payment.policy_id == Policy.id)
                    & (
                        Payment.payment_status
                        == "Success"
                    )
                ),
            )
            .group_by(
                Policy.id,
                Policy.policy_number,
                Policy.customer_id,
                Policy.premium_amount,
            )
            .order_by(Policy.id)
            .all()
        )

    @staticmethod
    def get_customer_policy_history(
        db: Session,
    ):
        return (
            db.query(
                Customer.id.label("customer_id"),
                Customer.full_name.label(
                    "customer_name"
                ),
                Policy.id.label("policy_id"),
                Policy.policy_number,
                Policy.plan_id,
                Policy.start_date,
                Policy.end_date,
                Policy.policy_status,
                Policy.premium_amount,
            )
            .join(
                Policy,
                Policy.customer_id == Customer.id,
            )
            .filter(
                Customer.is_deleted == False
            )
            .order_by(
                Customer.id,
                Policy.id,
            )
            .all()
        )

    @staticmethod
    def get_claim_settlement_report(
        db: Session,
    ):
        return (
            db.query(
                Claim.id.label("claim_id"),
                Claim.claim_number,
                Claim.customer_id,
                Claim.claim_amount,
                Claim.status.label("claim_status"),
                ClaimSettlement.settlement_amount,
                ClaimSettlement.settlement_status,
            )
            .outerjoin(
                ClaimSettlement,
                Claim.id
                == ClaimSettlement.claim_id,
            )
            .order_by(Claim.id)
            .all()
        )

    @staticmethod
    def get_agent_performance_report(
        db: Session,
    ):
        return (
            db.query(
                User.id.label("agent_id"),
                User.full_name.label(
                    "agent_name"
                ),
                func.count(Policy.id).label(
                    "total_policies"
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                Policy.policy_status
                                == "Active",
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("active_policies"),
                func.coalesce(
                    func.sum(
                        Policy.premium_amount
                    ),
                    0,
                ).label("total_premium"),
            )
            .outerjoin(
                Policy,
                Policy.agent_id == User.id,
            )
            .filter(
                User.role == "Insurance Agent"
            )
            .group_by(
                User.id,
                User.full_name,
            )
            .order_by(User.id)
            .all()
        )

    @staticmethod
    def get_monthly_premium_report(
        db: Session,
    ):
        return (
            db.query(
                func.strftime(
                    "%Y-%m",
                    Payment.payment_date,
                ).label("month"),
                func.coalesce(
                    func.sum(Payment.amount),
                    0,
                ).label(
                    "total_premium_collected"
                ),
            )
            .filter(
                Payment.payment_status == "Success"
            )
            .group_by(
                func.strftime(
                    "%Y-%m",
                    Payment.payment_date,
                )
            )
            .order_by(
                func.strftime(
                    "%Y-%m",
                    Payment.payment_date,
                )
            )
            .all()
        )

    @staticmethod
    def get_monthly_claim_report(
        db: Session,
    ):
        return (
            db.query(
                func.strftime(
                    "%Y-%m",
                    Claim.incident_date,
                ).label("month"),
                func.count(
                    Claim.id
                ).label("total_claims"),
                func.coalesce(
                    func.sum(
                        Claim.claim_amount
                    ),
                    0,
                ).label(
                    "total_claim_amount"
                ),
            )
            .group_by(
                func.strftime(
                    "%Y-%m",
                    Claim.incident_date,
                )
            )
            .order_by(
                func.strftime(
                    "%Y-%m",
                    Claim.incident_date,
                )
            )
            .all()
        )