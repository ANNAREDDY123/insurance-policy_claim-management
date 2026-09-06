from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.services.notification_service import create_notification


def send_notification_background(
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
):
    background_tasks.add_task(
        create_notification,
        db,
        user_id,
        notification_type,
        title,
        message,
    )