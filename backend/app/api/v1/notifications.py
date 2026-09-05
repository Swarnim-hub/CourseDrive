from typing import List
from fastapi import APIRouter, status
from sqlalchemy import select, update

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import NotFoundException
from app.models.notification import Notification
from app.schemas.notifications import NotificationMarkRead, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
@router.get("/", response_model=List[NotificationResponse], include_in_schema=False)
async def get_my_notifications(current_user: CurrentUserDep, db: SessionDep):
    """Retrieve all notifications for the current user."""
    query = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/read")
async def mark_notifications_read(
    data: NotificationMarkRead,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Mark specific notifications or all notifications as read."""
    if data.mark_all:
        stmt = (
            update(Notification)
            .where(Notification.user_id == current_user.id)
            .values(is_read=True)
        )
        await db.execute(stmt)
    elif data.notification_ids:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == current_user.id,
                Notification.id.in_(data.notification_ids),
            )
            .values(is_read=True)
        )
        await db.execute(stmt)
    await db.flush()
    return {"message": "Notifications updated"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Delete a notification."""
    notif = await db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    if not notif:
        raise NotFoundException("Notification", notification_id)
    await db.delete(notif)
    await db.flush()
