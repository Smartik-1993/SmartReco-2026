from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.models import Product
from app.services.dual_write import (
    create_product_dual_write,
    update_product_dual_write,
    delete_product_dual_write
)

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: Product, session: Session = Depends(get_session)):
    return create_product_dual_write(product, session)

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product_data: dict, session: Session = Depends(get_session)):
    try:
        return update_product_dual_write(product_id, product_data, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    delete_product_dual_write(product_id, session)
    return None