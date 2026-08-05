import json
from typing import Dict, Any
from app.agent.state import AgentState
from app.vector_db import get_product_collection
from app.core.mesh_client import mesh_client
from app.core.mesh_llm import get_mesh_llm
from langchain_core.messages import SystemMessage, HumanMessage

def summarize_user_events_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Synthesizes raw behavioral events into a focused semantic search query.
    """
    events_text = state.get("events_summary", "")
    if not events_text or events_text == "No recent activity":
        return {"should_recommend": False, "search_query": ""}

    # Use LLM or lightweight extraction to distill behavioral intent
    llm = get_mesh_llm()
    prompt = f"""You are a customer behavior analyzer.
Review the user's recent actions on our learning/product site:
{events_text}

Summarize what this user is interested in buying or learning about right now in a single, concise search query (10-15 words max).
Output ONLY the query string, nothing else.
"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        query = response.content.strip()
    except Exception:
        # Fallback if API key is mock
        query = "advanced topics and courses"

    return {"search_query": query, "should_recommend": True}

def vector_retrieval_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Queries ChromaDB vector database using the synthesized user query.
    """
    if not state.get("should_recommend"):
        return {"retrieved_products": []}

    search_query = state["search_query"]
    query_vector = mesh_client.get_embedding(search_query)

    collection = get_product_collection()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
        include=["documents", "metadatas"]
    )

    products = []
    if results and "metadatas" in results and results["metadatas"]:
        for meta in results["metadatas"][0]:
            products.append(meta)

    return {"retrieved_products": products}

def persuasive_narrative_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Generates compelling, catalog-grounded narrative explaining why recommendations fit the user.
    """
    products = state.get("retrieved_products", [])
    if not products:
        return {
            "narrative": "Explore our catalog to get personalized recommendations tailored to your journey!",
            "recommended_product_ids": []
        }

    product_context = "\n".join([
        f"- ID {p['product_id']}: {p['title']} ({p['category']}) - ${p['price']}"
        for p in products
    ])

    llm = get_mesh_llm()
    system_prompt = """You are SmartReco, an empathetic and persuasive learning guide.
Your goal is to write a short, motivating 2-3 sentence personalized pitch explaining why the suggested items match the user's recent browsing journey. Be specific, enthusiastic, and direct."""

    user_prompt = f"""User Recent Intent: {state['search_query']}
Matching Products Found:
{product_context}

Write a persuasive 2-3 sentence recommendation note addressing the user."""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        narrative = response.content.strip()
    except Exception:
        # Fallback for mock mode
        narrative = f"Based on your recent interest in '{state['search_query']}', we picked these top resources to accelerate your skills!"

    product_ids = [p["product_id"] for p in products]
    return {
        "narrative": narrative,
        "recommended_product_ids": product_ids
    }