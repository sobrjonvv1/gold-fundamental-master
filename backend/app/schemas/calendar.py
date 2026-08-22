from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EconomicEventResponse(BaseModel):
    id: int
    event_name: str
    event_type: Optional[str] = None
    currency: str
    country: str
    event_time: datetime
    impact: str
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
    previous_revision: Optional[str] = None
    surprise_val: Optional[float] = None
    gold_impact: Optional[str] = None
    source_url: Optional[str] = None
    provider: str

    model_config = ConfigDict(from_attributes=True)
