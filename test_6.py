# test_step6.py
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import init_db, engine
from sqlmodel import Session, select
from app.models import User, Event, Recommendation
from app.services.scheduler import process_pending_user_events

init_db()

with Session(engine) as session:
    print("--- 🛠️ 1. SEEDING USER BEHAVIOR FOR BACKGROUND SCHEDULER ---")
    
    # Fetch or create test user
    user = session.exec(select(User).where(User.email == "testuser@example.com")).first()
    if not user:
        user = User(email="testuser@example.com", password_hash="dummyhash")
        session.add(user)
        session.commit()
        session.refresh(user)

    # Log fresh search event
    e = Event(
        user_id=user.id,
        event_type="search",
        payload=json.dumps({"query": "FastAPI async microservices and event batching"})
    )
    session.add(e)
    session.commit()
    print(f"✅ Logged new event for User ID {user.id}")

    # Count recommendations prior to background worker
    initial_recs = len(session.exec(select(Recommendation).where(Recommendation.user_id == user.id)).all())

    print("\n--- 🛠️ 2. TRIGGERING BACKGROUND SCHEDULER TASK ---")
    process_pending_user_events()

    # Verify background worker created a new recommendation
    updated_recs = session.exec(select(Recommendation).where(Recommendation.user_id == user.id)).all()
    print(f"✅ Recommendations before: {initial_recs} | Recommendations after: {len(updated_recs)}")
    
    assert len(updated_recs) > initial_recs, "Scheduler failed to generate a new recommendation!"

    latest_rec = updated_recs[-1]
    print(f"✅ Latest Scheduled Recommendation Narrative:\n\"{latest_rec.narrative}\"\n")

print("🎉 ALL SCHEDULER & BACKGROUND WORKER TESTS PASSED SUCCESSFULLY!")