from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseEconomicCalendarProvider(ABC):
    @abstractmethod
    async def fetch_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Fetch economic calendar events within time window"""
        pass


class BaseFedProvider(ABC):
    @abstractmethod
    async def fetch_fed_events(self) -> List[Dict[str, Any]]:
        """Fetch recent Fed speeches, statements, and FOMC releases"""
        pass


class BaseMarketDataProvider(ABC):
    @abstractmethod
    async def fetch_market_observations() -> Dict[str, Dict[str, Any]]:
        """Fetch DXY, Yields (US2Y, US10Y, Real Yields) and Gold spot"""
        pass


class BaseNewsProvider(ABC):
    @abstractmethod
    async def fetch_latest_news(self) -> List[Dict[str, Any]]:
        """Fetch relevant financial & macro news"""
        pass
