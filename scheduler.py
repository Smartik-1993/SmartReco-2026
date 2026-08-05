import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from app.database import engine
from app.models import Event, User
from app.services.recommendation_service import generate_user_recommendation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smartreco.scheduler")

scheduler = BackgroundScheduler()

def process_pending_user_events():
    """
    Background task: Finds active users with recent events and runs the LangGraph recommendation agent.
    """
    logger.info("⏰ Running scheduled background recommendation generator...")
    
    with Session(engine) as session:
        # Find distinct users who have logged events
        statement = select(Event.user_id).distinct()
        active_user_ids = session.exec(statement).all()

        if not active_user_ids:
            logger.info("ℹ️ No active users with pending events found.")
            return

        for user_id in active_user_ids:
            try:
                logger.info(f"⚡ Processing recommendations for User ID {user_id}...")
                rec = generate_user_recommendation(user_id=user_id, session=session)
                logger.info(f"✅ Generated Rec ID {rec.id} for User ID {user_id}")
            except Exception as e:
                logger.error(f"❌ Error generating recs for User ID {user_id}: {e}")

def start_scheduler():
    """
    Starts the background scheduler loop.
    """
    # Run every 60 seconds (adjust interval for production)
    scheduler.add_job(
        process_pending_user_events,
        "interval",
        seconds=60,
        id="user_recommendation_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info("🚀 Background Recommendation Scheduler initialized successfully.")

def shutdown_scheduler():
    """
    Gracefully shuts down the scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Background Recommendation Scheduler stopped.")