import json
from sqlmodel import Session, select
from app.models import Event, Recommendation
from app.agent.graph import recommendation_agent

def generate_user_recommendation(user_id: int, session: Session) -> Recommendation:
    """
    Consumes user's unhandled events, executes LangGraph agent, and saves result.
    """
    # Fetch last 10 user events
    statement = (
        select(Event)
        .where(Event.user_id == user_id)
        .order_by(Event.timestamp.desc())
        .limit(10)
    )
    events = session.exec(statement).all()

    if not events:
        summary = "No recent activity"
    else:
        summary_lines = []
        for e in reversed(events):
            summary_lines.append(f"- Event: {e.event_type} | Details: {e.payload}")
        summary = "\n".join(summary_lines)

    # Execute LangGraph Agent
    initial_state = {
        "user_id": user_id,
        "events_summary": summary,
        "search_query": "",
        "retrieved_products": [],
        "narrative": "",
        "recommended_product_ids": [],
        "should_recommend": True
    }

    final_state = recommendation_agent.invoke(initial_state)

    # Persist recommendation to SQL
    rec = Recommendation(
        user_id=user_id,
        narrative=final_state["narrative"],
        recommended_product_ids=json.dumps(final_state["recommended_product_ids"])
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)

    return rec