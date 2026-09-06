from app.models.notification import Notification
from app.models.user import User
from app.services.notification_service import (
    create_notification,
    mark_notification_as_read,
)


def create_test_user(db):
    user = User(
        full_name="Notification Service User",
        email="notification_service@example.com",
        hashed_password="test-password",
        role="Customer",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =============================================================
# CREATE NOTIFICATION
# =============================================================

def test_create_notification(db_session):

    user = create_test_user(db_session)

    notification = create_notification(
        db=db_session,
        user_id=user.id,
        notification_type="POLICY_ACTIVATION",
        title="Policy Activated",
        message="Your insurance policy has been activated.",
    )

    assert notification.id is not None
    assert notification.user_id == user.id
    assert notification.notification_type == "POLICY_ACTIVATION"
    assert notification.title == "Policy Activated"
    assert notification.message == (
        "Your insurance policy has been activated."
    )
    assert notification.is_read is False


# =============================================================
# MARK NOTIFICATION AS READ
# =============================================================

def test_mark_notification_as_read(db_session):

    user = create_test_user(db_session)

    notification = Notification(
        user_id=user.id,
        notification_type="POLICY_ACTIVATION",
        title="Policy Activated",
        message="Your policy is active.",
        is_read=False,
    )

    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)

    updated_notification = mark_notification_as_read(
        db=db_session,
        notification=notification,
    )

    assert updated_notification.is_read is True
    assert updated_notification.read_at is not None