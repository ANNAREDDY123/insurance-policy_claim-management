from sqlalchemy.orm import Session

from app.models.claim_settlement import ClaimSettlement


class ClaimSettlementRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        settlement_id: int,
    ):
        return (
            db.query(ClaimSettlement)
            .filter(
                ClaimSettlement.id == settlement_id
            )
            .first()
        )

    @staticmethod
    def get_by_claim_id(
        db: Session,
        claim_id: int,
    ):
        return (
            db.query(ClaimSettlement)
            .filter(
                ClaimSettlement.claim_id == claim_id
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(ClaimSettlement)
            .order_by(
                ClaimSettlement.id
            )
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        settlement: ClaimSettlement,
    ):
        db.add(settlement)
        db.commit()
        db.refresh(settlement)

        return settlement