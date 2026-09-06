from sqlalchemy.orm import Session

from app.models.claim_document import ClaimDocument


class ClaimDocumentRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        document_id: int,
    ):
        return (
            db.query(ClaimDocument)
            .filter(
                ClaimDocument.id == document_id
            )
            .first()
        )

    @staticmethod
    def get_by_claim_id(
        db: Session,
        claim_id: int,
    ):
        return (
            db.query(ClaimDocument)
            .filter(
                ClaimDocument.claim_id == claim_id
            )
            .order_by(
                ClaimDocument.id
            )
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        document: ClaimDocument,
    ):
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def update(
        db: Session,
        document: ClaimDocument,
    ):
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def delete(
        db: Session,
        document: ClaimDocument,
    ):
        db.delete(document)
        db.commit()

        return document