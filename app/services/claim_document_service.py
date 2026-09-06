from sqlalchemy.orm import Session

from app.models.claim_document import ClaimDocument
from app.repositories.claim_document_repository import (
    ClaimDocumentRepository,
)


class ClaimDocumentService:

    @staticmethod
    def get_document(
        db: Session,
        document_id: int,
    ):
        return ClaimDocumentRepository.get_by_id(
            db=db,
            document_id=document_id,
        )

    @staticmethod
    def get_claim_documents(
        db: Session,
        claim_id: int,
    ):
        return ClaimDocumentRepository.get_by_claim_id(
            db=db,
            claim_id=claim_id,
        )

    @staticmethod
    def create_document(
        db: Session,
        document: ClaimDocument,
    ):
        return ClaimDocumentRepository.create(
            db=db,
            document=document,
        )

    @staticmethod
    def update_document(
        db: Session,
        document: ClaimDocument,
    ):
        return ClaimDocumentRepository.update(
            db=db,
            document=document,
        )

    @staticmethod
    def delete_document(
        db: Session,
        document: ClaimDocument,
    ):
        return ClaimDocumentRepository.delete(
            db=db,
            document=document,
        )