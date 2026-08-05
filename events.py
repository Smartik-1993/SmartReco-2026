from pydantic import BaseModel
from typing import List, Optional

class EventItemSchema(BaseModel):
    event_type: str  # "page_view", "search", "product_click", "dwell_time"
    payload: str     # JSON formatted string containing metadata

class EventBatchSchema(BaseModel):
    events: List[EventItemSchema]