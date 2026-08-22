from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FundamentalStateResponse(BaseModel):
    id: int
    instrument: str
    horizon: str
    bias: str
    strength: str
    main_driver: str
    supporting_factors: List[str]
    conflicting_factors: List[str]
    base_scenario: str
    alternative_scenario: str
    invalidation: str
    key_risks: List[str]
    next_catalyst: str
    data_quality: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class HorizonSummary(BaseModel):
    horizon: str
    bias: str
    strength: str
    main_driver: str
    last_update: datetime


class CurrentFundamentalOverview(BaseModel):
    instrument: str = "XAUUSD"
    horizons: List[HorizonSummary]
    current_view: FundamentalStateResponse
    drivers_summary: dict
