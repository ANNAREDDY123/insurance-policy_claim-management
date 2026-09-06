from datetime import datetime

from app.models.user import User
from app.models.notification import Notification

from app.utils.security import create_access_token


def create_test_user(db):
    user = User(
        full_name="Notification Test User",
        email="notification_test@example.com",
        hashed_password="test-password",
        role="Customer",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    return {
        "user": user,
        "headers": headers,
    }


def create_test_notification(
    db,
    user_id,
    notification_type="POLICY_ACTIVATION",
    title="Policy Activated",
    message="Your insurance policy has been activated successfully.",
    is_read=False,
):
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        is_read=is_read,
        read_at=datetime.utcnow() if is_read else None,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# =============================================================
# GET MY NOTIFICATIONS
# =============================================================

def test_get_my_notifications(client, db_session):

    data = create_test_user(db_session)

    create_test_notification(
        db_session,
        data["user"].id,
    )

    create_test_notification(
        db_session,
        data["user"].id,
        notification_type="PREMIUM_PAYMENT_SUCCESS",
        title="Premium Payment Successful",
        message="Your premium payment was successful.",
    )

    response = client.get(
        "/notifications",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) == 2

    notification_types = {
        item["notification_type"]
        for item in result
    }

    assert "POLICY_ACTIVATION" in notification_types
    assert "PREMIUM_PAYMENT_SUCCESS" in notification_types


# =============================================================
# GET UNREAD NOTIFICATIONS
# =============================================================

def test_get_unread_notifications(client, db_session):

    data = create_test_user(db_session)

    create_test_notification(
        db_session,
        data["user"].id,
        notification_type="POLICY_ACTIVATION",
        title="Policy Activated",
        message="Your policy is active.",
        is_read=False,
    )

    create_test_notification(
        db_session,
        data["user"].id,
        notification_type="CLAIM_APPROVED",
        title="Claim Approved",
        message="Your claim has been approved.",
        is_read=True,
    )

    response = client.get(
        "/notifications/unread",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result) == 1
    assert result[0]["notification_type"] == "POLICY_ACTIVATION"
    assert result[0]["is_read"] is False


# =============================================================
# MARK NOTIFICATION AS READ
# =============================================================

def test_mark_notification_as_read(client, db_session):

    data = create_test_user(db_session)

    notification = create_test_notification(
        db_session,
        data["user"].id,
        is_read=False,
    )

    response = client.post(
        f"/notifications/{notification.id}/read",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert result["message"] == "Notification marked as read"

    db_session.refresh(notification)

    assert notification.is_read is True
    assert notification.read_at is not None


# =============================================================
# MARK ALL NOTIFICATIONS AS READ
# =============================================================

def test_mark_all_notifications_as_read(client, db_session):

    data = create_test_user(db_session)

    notification_1 = create_test_notification(
        db_session,
        data["user"].id,
        notification_type="POLICY_ACTIVATION",
        is_read=False,
    )

    notification_2 = create_test_notification(
        db_session,
        data["user"].id,
        notification_type="CLAIM_SUBMITTED",
        title="Claim Submitted",
        message="Your claim has been submitted.",
        is_read=False,
    )

    response = client.post(
        "/notifications/read-all",
        headers=data["headers"],
    )

    assert response.status_code == 200

    result = response.json()

    assert result["message"] == "All notifications marked as read"

    db_session.refresh(notification_1)
    db_session.refresh(notification_2)

    assert notification_1.is_read is True
    assert notification_1.read_at is not None

    assert notification_2.is_read is True
    assert notification_2.read_at is not None


# =============================================================
# USER CANNOT ACCESS ANOTHER USER'S NOTIFICATION
# =============================================================

def test_user_cannot_mark_other_users_notification_as_read(
    client,
    db_session,
):

    user_1 = create_test_user(db_session)

    notification = create_test_notification(
        db_session,
        user_1["user"].id,
    )

    user_2 = User(
        full_name="Second Notification User",
        email="notification_test_2@example.com",
        hashed_password="test-password",
        role="Customer",
        is_active=True,
    )

    db_session.add(user_2)
    db_session.commit()
    db_session.refresh(user_2)

    access_token = create_access_token(
        user_id=user_2.id,
        role=user_2.role,
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = client.post(
        f"/notifications/{notification.id}/read",
        headers=headers,
    )

    assert response.status_code == 404

    db_session.refresh(notification)

    assert notification.is_read is False


# =============================================================
# UNAUTHENTICATED ACCESS
# =============================================================
def test_notifications_require_authentication(client):

    response = client.get("/notifications")

    assert response.status_code == 401