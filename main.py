import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.routers import admin, events, web
from app.services.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    init_db()
    start_scheduler()
    yield
    # Shutdown phase
    shutdown_scheduler()

app = FastAPI(title="SmartReco - Agentic Recommendation Platform", lifespan=lifespan)

# Static file mounting
os.makedirs("app/static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Router registration
app.include_router(web.router)
app.include_router(events.router)
app.include_router(admin.router, prefix="/api/admin")