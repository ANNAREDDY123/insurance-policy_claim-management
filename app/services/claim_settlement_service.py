from sqlalchemy.orm import Session

from app.models.claim_settlement import ClaimSettlement
from app.repositories.claim_settlement_repository import (
    ClaimSettlementRepository,
)


class ClaimSettlementService:

    @staticmethod
    def get_settlement(
        db: Session,
        settlement_id: int,
    ):
        return ClaimSettlementRepository.get_by_id(
            db=db,
            settlement_id=settlement_id,
        )

    @staticmethod
    def get_settlement_by_claim_id(
        db: Session,
        claim_id: int,
    ):
        return ClaimSettlementRepository.get_by_claim_id(
            db=db,
            claim_id=claim_id,
        )

    @staticmethod
    def get_settlements(
        db: Session,
    ):
        return ClaimSettlementRepository.get_all(
            db=db,
        )

    @staticmethod
    def create_settlement(
        db: Session,
        settlement: ClaimSettlement,
    ):
        return ClaimSettlementRepository.create(
            db=db,
            settlement=settlement,
        )