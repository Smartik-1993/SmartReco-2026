import os
import logging
from langchain_openai import ChatOpenAI
from app.core.config import settings

logger = logging.getLogger("smartreco.mesh_llm")

def get_mesh_llm():
    """
    Creates an OpenAI-compatible ChatOpenAI model configured to route 
    requests through Mesh API (api.meshapi.ai).
    """
    api_key = os.getenv("MESH_API_KEY", getattr(settings, "MESH_API_KEY", "mock_mesh_api_key"))
    
    # Fallback to standard OpenAI or mock if key is not configured
    if not api_key or api_key in ("mock_mesh_api_key", "your_mesh_api_key_here"):
        api_key = "mock_mesh_api_key"

    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
        base_url="https://api.meshapi.ai/v1",
        temperature=0.7,
        max_retries=1,
        request_timeout=10
    )