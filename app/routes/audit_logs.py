from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.dependencies import get_current_user, require_roles


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Super Admin")
    ),
):
    audit_logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return audit_logs