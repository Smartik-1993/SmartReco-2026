# SmartReco-2026

**Overview of Tech-stack**

┌────────────────────────────────────────────────────────┐
                  │                    Frontend (Jinja2)                   │
                  │  * Non-blocking JS tracking engine (navigator.sendBeacon) │
                  └──────────────────────────┬─────────────────────────────┘
                                             │
                                   Batch HTTP / Async POST
                                             │
                                             ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                    FastAPI Backend                     │
                  │  * Auth & CRUD Routes                                  │
                  │  * Background Tasks (FastAPI / Celery)                │
                  └────────────┬─────────────────────────────┬─────────────┘
                               │                             │
                      Dual-Write / Sync             Fetch History / Write Output
                               │                             │
                               ▼                             ▼
                  ┌─────────────────────────┐   ┌──────────────────────────┐
                  │ PostgreSQL / SQLite     │   │ ChromaDB / Qdrant        │
                  │ (Users, Products,       │   │ (Product Embeddings +    │
                  │  Events, Recs)          │   │  Semantic Metadata)      │
                  └─────────────────────────┘   └─────────────┬────────────┘
                                                              │
                                                        Semantic RAG
                                                              │
                                                              ▼
                                                ┌──────────────────────────┐
                                                │ LangGraph Agent          │
                                                │ (Mesh API / LangSmith)   │
                                                └──────────────────────────┘


Backend: FastAPI (Async out-of-the-box handles batch events smoothly).

Frontend: Jinja2 templates + Tailwind CSS + Vanilla JS event tracer.

Primary DB: PostgreSQL (via SQLAlchemy / SQLModel) or SQLite for fast local setup.

Vector DB: ChromaDB (embedded, zero infra setup) or Qdrant.

Agent Framework: LangGraph (Bonus ⭐) + Mesh API client + LangSmith tracing.

Background Jobs: APScheduler (Bonus ⭐ - minimal setup for proactive emails).                                                
