from fastapi import APIRouter, Depends, status, Request
from sqlmodel import Session
from app.database import get_session
from app.models import Event
from app.schemas.events import EventBatchSchema

router = APIRouter(prefix="/api/v1/events", tags=["Behavioral Events"])

@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
async def receive_event_batch(
    batch: EventBatchSchema,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Non-blocking ingestion endpoint.
    Receives batched behavioral events and bulk inserts them into SQL.
    """
    # Retrieve user ID (Assume default mock user ID 1 if auth session not active)
    user_id = getattr(request.state, "user_id", 1)

    db_events = [
        Event(
            user_id=user_id,
            event_type=item.event_type,
            payload=item.payload
        )
        for item in batch.events
    ]

    # Bulk save events efficiently
    session.add_all(db_events)
    session.commit()

    return {"status": "success", "processed_count": len(db_events)}