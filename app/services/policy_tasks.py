from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.services.notification_service import create_notification


def send_policy_expiry_reminders(
    db: Session,
    user_id: int,
    days_before_expiry: int = 30,
):
    today = date.today()
    reminder_date = today + timedelta(
        days=days_before_expiry
    )

    policies = (
        db.query(Policy)
        .filter(
            Policy.policy_status == "Active",
            Policy.end_date == reminder_date,
        )
        .all()
    )

    notifications_created = 0

    for policy in policies:
        create_notification(
            db=db,
            user_id=user_id,
            notification_type="POLICY_EXPIRY",
            title="Policy Expiry Reminder",
            message=(
                f"Your policy {policy.policy_number} "
                f"will expire on {policy.end_date}. "
                f"Please renew your policy before the "
                f"expiry date."
            ),
        )

        notifications_created += 1

    return notifications_created