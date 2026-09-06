from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.claim_document import ClaimDocument
from app.models.user import User
from app.schemas.claim_document import (
    VERIFICATION_STATUSES,
    ClaimDocumentCreate,
    ClaimDocumentResponse,
    ClaimDocumentUpdate,
    ClaimDocumentVerify,
)
from app.services.claim_document_service import (
    ClaimDocumentService,
)
from app.services.claim_service import ClaimService
from app.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/claims",
    tags=["Claim Documents"],
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


def get_document_or_404(
    db: Session,
    document_id: int,
):
    document = ClaimDocumentService.get_document(
        db=db,
        document_id=document_id,
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Claim document not found",
        )

    return document


def validate_verification_status(
    verification_status: str,
):
    if verification_status not in VERIFICATION_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification status",
        )


def document_response(
    document: ClaimDocument,
):
    return {
        "id": document.id,
        "claim_id": document.claim_id,
        "document_type": document.document_type,
        "file_name": document.file_name,
        "file_path": document.file_path,
        "description": document.description,

        # Level 8 field
        "verification_status": (
            document.verification_status
        ),

        # Existing test compatibility
        "status": document.status,

        "uploaded_at": document.uploaded_at,
    }


# ============================================================
# UPLOAD CLAIM DOCUMENT
# ============================================================

@router.post(
    "/{claim_id}/documents",
    response_model=ClaimDocumentResponse,
)
def upload_claim_document(
    claim_id: int,
    document_data: ClaimDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Customer",
        )
    ),
):
    get_claim_or_404(
        db=db,
        claim_id=claim_id,
    )

    document = ClaimDocument(
        claim_id=claim_id,
        document_type=document_data.document_type,
        file_name=document_data.file_name,
        file_path=document_data.file_path,
        description=document_data.description,

        # Existing workflow
        status="Uploaded",

        # Level 8 workflow
        verification_status="Pending",
    )

    document = ClaimDocumentService.create_document(
        db=db,
        document=document,
    )

    return document_response(document)


# ============================================================
# GET CLAIM DOCUMENTS
# ============================================================

@router.get(
    "/{claim_id}/documents",
    response_model=list[ClaimDocumentResponse],
)
def get_claim_documents(
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

    documents = (
        ClaimDocumentService.get_claim_documents(
            db=db,
            claim_id=claim_id,
        )
    )

    return [
        document_response(document)
        for document in documents
    ]


# ============================================================
# GET SINGLE DOCUMENT
# ============================================================

@router.get(
    "/documents/{document_id}",
    response_model=ClaimDocumentResponse,
)
def get_claim_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    document = get_document_or_404(
        db=db,
        document_id=document_id,
    )

    return document_response(document)


# ============================================================
# UPDATE CLAIM DOCUMENT
# ============================================================

@router.put(
    "/documents/{document_id}",
    response_model=ClaimDocumentResponse,
)
def update_claim_document(
    document_id: int,
    document_data: ClaimDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Customer",
        )
    ),
):
    document = get_document_or_404(
        db=db,
        document_id=document_id,
    )

    if document_data.document_type is not None:
        document.document_type = (
            document_data.document_type
        )

    if document_data.description is not None:
        document.description = (
            document_data.description
        )

    # Existing tests use "status"
    if document_data.status is not None:
        document.status = document_data.status

        # Keep verification status synchronized
        document.verification_status = (
            document_data.status
        )

    document = ClaimDocumentService.update_document(
        db=db,
        document=document,
    )

    return document_response(document)


# ============================================================
# VERIFY CLAIM DOCUMENT
# ============================================================

@router.put(
    "/documents/{document_id}/verify",
    response_model=ClaimDocumentResponse,
)
def verify_claim_document(
    document_id: int,
    verification_data: ClaimDocumentVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Claims Officer",
        )
    ),
):
    document = get_document_or_404(
        db=db,
        document_id=document_id,
    )

    validate_verification_status(
        verification_data.verification_status
    )

    document.verification_status = (
        verification_data.verification_status
    )

    document.status = (
        verification_data.verification_status
    )

    document = ClaimDocumentService.update_document(
        db=db,
        document=document,
    )

    return document_response(document)


# ============================================================
# DELETE CLAIM DOCUMENT
# ============================================================

@router.delete(
    "/documents/{document_id}",
)
def delete_claim_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Super Admin",
            "Customer",
        )
    ),
):
    document = get_document_or_404(
        db=db,
        document_id=document_id,
    )

    ClaimDocumentService.delete_document(
        db=db,
        document=document,
    )

    return {
        "message": (
            "Claim document deleted successfully"
        )
    }