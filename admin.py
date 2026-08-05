# app/routers/admin.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func
from app.database import get_session
from app.models import User, Event, Recommendation
from app.services.scheduler import process_pending_user_events

router = APIRouter(tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin")
async def render_admin_dashboard(
    request: Request,
    session: Session = Depends(get_session)
):
    # Fetch metrics
    user_count = session.exec(select(func.count(User.id))).one()
    event_count = session.exec(select(func.count(Event.id))).one()
    rec_count = session.exec(select(func.count(Recommendation.id))).one()

    # Recent activity logs
    recent_events = session.exec(
        select(Event).order_by(Event.id.desc()).limit(15)
    ).all()

    recent_recommendations = session.exec(
        select(Recommendation).order_by(Recommendation.id.desc()).limit(10)
    ).all()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "metrics": {
                "user_count": user_count,
                "event_count": event_count,
                "recommendation_count": rec_count,
            },
            "recent_events": recent_events,
            "recent_recommendations": recent_recommendations,
        }
    )


@router.post("/trigger-scheduler")
async def manual_trigger_scheduler():
    """Manually triggers the background scheduler pipeline."""
    process_pending_user_events()
    return RedirectResponse(url="/api/admin/admin", status_code=303)