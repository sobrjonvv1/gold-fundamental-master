from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class LLMAnalysisOutput(BaseModel):
    bias: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    strength: Literal["STRONG", "MODERATE", "WEAK"]
    main_driver: str = Field(..., description="Key fundamental reasoning for the view")
    supporting_factors: List[str] = Field(default_factory=list)
    conflicting_factors: List[str] = Field(default_factory=list)
    base_scenario: str = Field(..., description="Base fundamental scenario")
    alternative_scenario: str = Field(..., description="Alternative fundamental scenario")
    invalidation: str = Field(..., description="Key fundamental trigger invalidating base scenario")
    key_risks: List[str] = Field(default_factory=list)
    next_catalyst: str = Field(..., description="Upcoming key event/catalyst")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
