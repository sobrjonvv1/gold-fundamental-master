from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    alert_settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EconomicEvent(Base):
    __tablename__ = "economic_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column(String(255), index=True)
    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), index=True, default="USD")
    country: Mapped[str] = mapped_column(String(50), default="US")
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    impact: Mapped[str] = mapped_column(String(20), index=True) # HIGH, MEDIUM, LOW
    actual: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    forecast: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    previous: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    previous_revision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    surprise_val: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gold_impact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # BULLISH, BEARISH, NEUTRAL
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(50), default="forex_factory")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class NewsEvent(Base):
    __tablename__ = "news_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    headline: Mapped[str] = mapped_column(Text)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    gold_relevance: Mapped[str] = mapped_column(String(20), default="MEDIUM") # HIGH, MEDIUM, LOW
    impact_bias: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # BULLISH, BEARISH, NEUTRAL
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FedEvent(Base):
    __tablename__ = "fed_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_title: Mapped[str] = mapped_column(String(255))
    speaker_or_type: Mapped[str] = mapped_column(String(100)) # Powell, FOMC Statement, Minutes
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    stance: Mapped[str] = mapped_column(String(20)) # HAWKISH, DOVISH, NEUTRAL, MIXED
    summary: Mapped[Text] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MarketObservation(Base):
    __tablename__ = "market_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument: Mapped[str] = mapped_column(String(20), index=True) # DXY, US2Y, US10Y, REAL_YIELD, XAUUSD
    value: Mapped[float] = mapped_column(Float)
    change_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    direction: Mapped[str] = mapped_column(String(20)) # UP, DOWN, FLAT
    driver: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source: Mapped[str] = mapped_column(String(50), default="market_data")


class GeopoliticalEvent(Base):
    __tablename__ = "geopolitical_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100)) # WAR, SANCTIONS, TARIFFS, ELECTION
    countries: Mapped[List[str]] = mapped_column(JSON)
    severity: Mapped[str] = mapped_column(String(20)) # LOW, MEDIUM, HIGH, CRITICAL
    risk_direction: Mapped[str] = mapped_column(String(20)) # RISK_UP, RISK_DOWN, NEUTRAL
    gold_relevance: Mapped[str] = mapped_column(String(20)) # HIGH, MEDIUM, LOW
    description: Mapped[Text] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class GoldDemandData(Base):
    __tablename__ = "gold_demand_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50)) # CENTRAL_BANK, ETF_FLOWS, COT_POSITIONING
    metric_name: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20)) # TONNES, CONTRACTS, USD_MILLIONS
    period: Mapped[str] = mapped_column(String(50))
    bias_impact: Mapped[str] = mapped_column(String(20)) # BULLISH, BEARISH, NEUTRAL
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class FundamentalState(Base):
    __tablename__ = "fundamental_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument: Mapped[str] = mapped_column(String(20), default="XAUUSD", index=True)
    horizon: Mapped[str] = mapped_column(String(20), index=True) # MONTH, WEEK, DAY, SESSION_ASIA, SESSION_LONDON, SESSION_NEW_YORK
    bias: Mapped[str] = mapped_column(String(20), index=True) # BULLISH, BEARISH, NEUTRAL
    strength: Mapped[str] = mapped_column(String(20)) # STRONG, MODERATE, WEAK
    main_driver: Mapped[str] = mapped_column(Text)
    supporting_factors: Mapped[List[str]] = mapped_column(JSON)
    conflicting_factors: Mapped[List[str]] = mapped_column(JSON)
    base_scenario: Mapped[Text] = mapped_column(Text)
    alternative_scenario: Mapped[Text] = mapped_column(Text)
    invalidation: Mapped[Text] = mapped_column(Text)
    key_risks: Mapped[List[str]] = mapped_column(JSON)
    next_catalyst: Mapped[str] = mapped_column(String(255))
    data_quality: Mapped[str] = mapped_column(String(20), default="GOOD") # GOOD, STALE, DEGRADED
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))


class FundamentalStateChange(Base):
    __tablename__ = "fundamental_state_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    horizon: Mapped[str] = mapped_column(String(20), index=True)
    previous_bias: Mapped[str] = mapped_column(String(20))
    new_bias: Mapped[str] = mapped_column(String(20))
    reason: Mapped[Text] = mapped_column(Text)
    trigger_event: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(50), index=True) # REGIME_CHANGE, HIGH_IMPACT_NEWS, SCHEDULED_REPORT
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[Text] = mapped_column(Text)
    event_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    horizon: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class LLMRequest(Base):
    __tablename__ = "llm_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(100))
    request_type: Mapped[str] = mapped_column(String(50)) # SYNTHESIS, NEWS_CLASSIFY, GEOPOLITICS
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20)) # SUCCESS, ERROR, CACHED, RATE_LIMITED
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))


class SystemHealth(Base):
    __tablename__ = "system_health"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component: Mapped[str] = mapped_column(String(50), index=True) # DB, REDIS, CALENDAR, FED, LLM
    status: Mapped[str] = mapped_column(String(20)) # ONLINE, DEGRADED, OFFLINE
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_check: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
