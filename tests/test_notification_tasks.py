from app.models.notification import Notification
from app.models.user import User
from app.services.notification_tasks import (
    send_notification_background,
)


def create_test_user(db):
    user = User(
        full_name="Background Task User",
        email="background_task@example.com",
        hashed_password="test-password",
        role="Customer",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =============================================================
# BACKGROUND NOTIFICATION TASK
# =============================================================

def test_send_notification_background(
    db_session,
    background_tasks,
):
    user = create_test_user(db_session)

    send_notification_background(
        background_tasks=background_tasks,
        db=db_session,
        user_id=user.id,
        notification_type="POLICY_ACTIVATION",
        title="Policy Activated",
        message="Your policy has been activated.",
    )

    # Execute the queued background task
    for task in background_tasks.tasks:
        task.func(*task.args, **task.kwargs)

    notification = (
        db_session.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.notification_type
            == "POLICY_ACTIVATION",
        )
        .first()
    )

    assert notification is not None
    assert notification.title == "Policy Activated"
    assert notification.message == (
        "Your policy has been activated."
    )
    assert notification.is_read is False