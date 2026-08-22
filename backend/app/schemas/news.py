from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NewsEventResponse(BaseModel):
    id: int
    headline: str
    body: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    published_at: datetime
    gold_relevance: str
    impact_bias: Optional[str] = None
    ai_summary: Optional[str] = None
    content_hash: str

    model_config = ConfigDict(from_attributes=True)
