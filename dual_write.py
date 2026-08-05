from sqlmodel import Session
from app.models import Product
from app.vector_db import get_product_collection
from app.core.mesh_client import mesh_client

def format_product_text(product: Product) -> str:
    """Construct rich semantic text string for embedding."""
    return f"Title: {product.title}. Category: {product.category}. Description: {product.description}. Price: ${product.price}"

def create_product_dual_write(product: Product, session: Session) -> Product:
    # 1. Commit to SQL primary store
    session.add(product)
    session.commit()
    session.refresh(product)

    # 2. Compute embedding & Write to ChromaDB
    text_content = format_product_text(product)
    vector = mesh_client.get_embedding(text_content)
    
    collection = get_product_collection()
    collection.add(
        ids=[str(product.id)],
        embeddings=[vector],
        documents=[text_content],
        metadatas=[{
            "product_id": product.id,
            "title": product.title,
            "category": product.category,
            "price": product.price
        }]
    )
    return product

def update_product_dual_write(product_id: int, updated_data: dict, session: Session) -> Product:
    # 1. Update SQL record
    product = session.get(Product, product_id)
    if not product:
        raise ValueError("Product not found")

    for key, value in updated_data.items():
        setattr(product, key, value)
        
    session.add(product)
    session.commit()
    session.refresh(product)

    # 2. Re-compute embedding & Update ChromaDB vector
    text_content = format_product_text(product)
    vector = mesh_client.get_embedding(text_content)
    
    collection = get_product_collection()
    collection.upsert(
        ids=[str(product.id)],
        embeddings=[vector],
        documents=[text_content],
        metadatas=[{
            "product_id": product.id,
            "title": product.title,
            "category": product.category,
            "price": product.price
        }]
    )
    return product

def delete_product_dual_write(product_id: int, session: Session) -> None:
    # 1. Delete from SQL
    product = session.get(Product, product_id)
    if product:
        session.delete(product)
        session.commit()

    # 2. Remove from ChromaDB
    collection = get_product_collection()
    collection.delete(ids=[str(product_id)])