from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class AgentState(TypedDict):
    user_id: int
    events_summary: str
    search_query: str
    retrieved_products: List[Dict[str, Any]]
    narrative: str
    recommended_product_ids: List[int]
    should_recommend: bool