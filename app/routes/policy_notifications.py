from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.policy_tasks import (
    send_policy_expiry_reminders,
)
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/policy-notifications",
    tags=["Policy Notifications"],
)


# ============================================================
# POLICY EXPIRY REMINDER
# ============================================================

@router.post("/expiry-reminder")
def trigger_policy_expiry_reminder(
    background_tasks: BackgroundTasks,
    days_before_expiry: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    background_tasks.add_task(
        send_policy_expiry_reminders,
        db,
        current_user.id,
        days_before_expiry,
    )

    return {
        "message": (
            "Policy expiry reminder task "
            "has been scheduled"
        ),
        "days_before_expiry": days_before_expiry,
    }