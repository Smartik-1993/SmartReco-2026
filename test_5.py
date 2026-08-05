# test_step5.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, engine
from sqlmodel import Session, select
from app.models import Product
from app.services.dual_write import create_product_dual_write

init_db()

# Seed a product if it does not already exist, and use its actual ID for the detail view
with Session(engine) as session:
    product = session.exec(
        select(Product).where(Product.title == "FastAPI Microservices Architecture")
    ).first()
    if not product:
        product = Product(
            title="FastAPI Microservices Architecture",
            description="Learn to build high-speed REST & GraphQL APIs with Python.",
            category="Backend Engineering",
            price=79.99
        )
        create_product_dual_write(product, session)

product_id = product.id
client = TestClient(app)

print("--- 🛠️ TESTING FASTAPI WEB STOREFRONT ROUTES ---")

# 1. Test Index View
response = client.get("/")
print(f"✅ Index Page Status: {response.status_code}")
assert response.status_code == 200
assert "SmartReco" in response.text

# 2. Test Product Detail View
response = client.get(f"/product/{product_id}")
print(f"✅ Product Detail Page Status: {response.status_code}")
assert response.status_code == 200
assert "FastAPI Microservices Architecture" in response.text

print("\n🎉 ALL STEP 5 FRONTEND & WEB ROUTE TESTS PASSED SUCCESSFULLY!")