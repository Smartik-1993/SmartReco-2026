import json
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models import Product, User, Recommendation
from app.services.recommendation_service import generate_user_recommendation

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def get_current_user_id(request: Request) -> int:
    """
    Helper to fetch or simulate active user session.
    In production, replace with real auth session logic.
    """
    return getattr(request.state, "user_id", 1)

@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Main Storefront catalog view with optional search filter.
    """
    user_id = get_current_user_id(request)

    # 1. Fetch catalog items
    query = select(Product)
    if search:
        query = query.where(Product.title.contains(search) | Product.description.contains(search))
    products = session.exec(query).all()

    # 2. Fetch latest recommendation for active user
    rec = session.exec(
        select(Recommendation)
        .where(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc())
    ).first()

    recommended_products = []
    narrative = None

    if rec:
        narrative = rec.narrative
        try:
            rec_ids = json.loads(rec.recommended_product_ids)
            if rec_ids:
                recommended_products = session.exec(
                    select(Product).where(Product.id.in_(rec_ids))
                ).all()
        except Exception:
            recommended_products = []

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "products": products,
            "search": search or "",
            "narrative": narrative,
            "recommended_products": recommended_products,
            "user_id": user_id
        }
    )

@router.get("/product/{product_id}", response_class=HTMLResponse)
def product_detail(
    product_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Product detail view with automated behavioral event context.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    user_id = get_current_user_id(request)

    return templates.TemplateResponse(
        request,
        "detail.html",
        {
            "request": request,
            "product": product,
            "user_id": user_id
        }
    )

@router.post("/trigger-recommendation", response_class=HTMLResponse)
def trigger_recommendation(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    On-demand agent execution route to refresh recommendations based on recent events.
    """
    user_id = get_current_user_id(request)
    generate_user_recommendation(user_id=user_id, session=session)
    
    # Redirect back to index view
    return index(request=request, search=None, session=session)