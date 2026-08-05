# app/routers/web.py
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.database import get_session
from app.models import Recommendation

router = APIRouter(tags=["Web Pages"])
templates = Jinja2Templates(directory="app/templates")

# Sample product dataset
CATALOG_PRODUCTS = [
    {"id": 1, "title": "Mesh API Integration Guide", "description": "Learn agentic orchestration with Mesh API and FastAPI."},
    {"id": 2, "title": "Vector Search Masterclass", "description": "High-performance vector retrieval with ChromaDB and HNSW."},
    {"id": 3, "title": "FastAPI Microservices", "description": "Asynchronous microservice design patterns in Python 3.11."},
    {"id": 4, "title": "LangGraph Recommendation Pipelines", "description": "Building contextual agentic AI recommenders from user events."},
]


@router.get("/")
async def render_home(
    request: Request,
    q: str = None,
    session: Session = Depends(get_session)
):
    user_id = 1  # Active session context

    # Filter products if a search query 'q' was provided
    if q and q.strip():
        search_term = q.lower().strip()
        filtered_products = [
            p for p in CATALOG_PRODUCTS
            if search_term in p["title"].lower() or search_term in p["description"].lower()
        ]
        # Fallback: if search query has no direct title match, still display all items so UI isn't empty
        display_products = filtered_products if filtered_products else CATALOG_PRODUCTS
    else:
        display_products = CATALOG_PRODUCTS

    # Fetch recent recommendations for User 1
    recommendations = session.exec(
        select(Recommendation)
        .where(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc())
    ).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "query": q,
            "products": display_products,
            "recommendations": recommendations,
        }
    )