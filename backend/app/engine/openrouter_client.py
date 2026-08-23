import httpx
import json
import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.core.redis import get_redis
from app.schemas.llm import LLMAnalysisOutput

logger = logging.getLogger("gold_fundamental.openrouter")


class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.fallback_model = settings.OPENROUTER_FALLBACK_MODEL
        self.daily_limit = settings.LLM_DAILY_REQUEST_LIMIT

    async def _check_and_increment_daily_budget(self) -> bool:
        """Check if daily LLM budget has been exceeded"""
        try:
            redis = await get_redis()
            today_key = f"llm_budget:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
            current_count = await redis.get(today_key)
            if current_count and int(current_count) >= self.daily_limit:
                logger.warning(f"Daily LLM request limit reached: {current_count}/{self.daily_limit}")
                return False
            await redis.incr(today_key)
            await redis.expire(today_key, 86400 * 2)
            return True
        except Exception as e:
            logger.warning(f"Error checking LLM budget in Redis: {e}")
            return True

    async def generate_fundamental_analysis(
        self,
        horizon: str,
        context_data: Dict[str, Any]
    ) -> LLMAnalysisOutput:
        """
        Sends structured compact context to LLM via OpenRouter.
        Validates strict JSON with Pydantic.
        """
        if settings.MOCK_MODE or not self.api_key:
            logger.info("MOCK_MODE=True or missing OPENROUTER_API_KEY -> returning mock LLM analysis")
            return self._get_mock_analysis(horizon, context_data)

        # Cache lookup
        prompt_hash = hashlib.sha256(json.dumps(context_data, sort_keys=True).encode()).hexdigest()
        cache_key = f"llm_cache:{horizon}:{prompt_hash}"
        try:
            redis = await get_redis()
            cached_res = await redis.get(cache_key)
            if cached_res:
                logger.info(f"LLM cache hit for horizon {horizon}")
                return LLMAnalysisOutput.model_validate_json(cached_res)
        except Exception as ce:
            logger.warning(f"Redis cache check failed: {ce}")

        # Check daily budget
        if not await self._check_and_increment_daily_budget():
            logger.warning("Daily LLM budget exhausted, returning fallback analysis")
            return self._get_mock_analysis(horizon, context_data)

        prompt = self._build_prompt(horizon, context_data)
        
        # Try primary model, fallback model if error
        response_json = await self._call_openrouter(self.model, prompt)
        if not response_json:
            logger.warning(f"Primary model {self.model} failed, trying fallback {self.fallback_model}")
            response_json = await self._call_openrouter(self.fallback_model, prompt)

        if not response_json:
            logger.error("All OpenRouter models failed. Returning mock fallback analysis.")
            return self._get_mock_analysis(horizon, context_data)

        # Validate response with Pydantic
        try:
            validated = LLMAnalysisOutput.model_validate_json(response_json)
            # Save to cache
            try:
                redis = await get_redis()
                await redis.set(cache_key, validated.model_dump_json(), ex=1800)
            except Exception:
                pass
            return validated
        except Exception as ve:
            logger.error(f"Pydantic validation failed for LLM response: {ve}. Response: {response_json}")
            # Retry once with correction prompt
            corrected_json = await self._retry_with_correction(response_json, str(ve))
            if corrected_json:
                try:
                    return LLMAnalysisOutput.model_validate_json(corrected_json)
                except Exception:
                    pass
            return self._get_mock_analysis(horizon, context_data)

    async def _call_openrouter(self, model: str, prompt: str) -> Optional[str]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://goldfundamentalmaster.com",
            "X-Title": "GOLD FUNDAMENTAL MASTER",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a Senior Quantitative Macro Research Analyst specializing ONLY in Gold (XAU/USD) fundamental analysis. "
                        "Do NOT use technical indicators, RSI, MACD, or candlestick patterns. "
                        "Output strictly VALID JSON matching the required schema with no extra prose, markdown wrappers, or explanation."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return content
                else:
                    logger.error(f"OpenRouter API error HTTP {resp.status_code}: {resp.text}")
                    return None
        except Exception as e:
            logger.error(f"HTTP exception during OpenRouter call: {e}")
            return None

    async def _retry_with_correction(self, raw_invalid_json: str, error_msg: str) -> Optional[str]:
        correction_prompt = (
            f"Your previous JSON output was invalid.\n"
            f"Error: {error_msg}\n"
            f"Previous output: {raw_invalid_json}\n"
            f"Please output strictly valid JSON conforming to LLMAnalysisOutput schema."
        )
        return await self._call_openrouter(self.model, correction_prompt)

    def _build_prompt(self, horizon: str, context_data: Dict[str, Any]) -> str:
        return f"""
Analyze XAU/USD (Gold) fundamentals for Horizon: {horizon}.

Context Data:
{json.dumps(context_data, indent=2)}

Required JSON Schema format:
{{
  "bias": "BULLISH" | "BEARISH" | "NEUTRAL",
  "strength": "STRONG" | "MODERATE" | "WEAK",
  "main_driver": "Short string explanation of core fundamental driver",
  "supporting_factors": ["Factor 1", "Factor 2"],
  "conflicting_factors": ["Factor 1"],
  "base_scenario": "Comprehensive base scenario description",
  "alternative_scenario": "Alternative scenario description",
  "invalidation": "Fundamental invalidation trigger",
  "key_risks": ["Risk 1", "Risk 2"],
  "next_catalyst": "Next major economic event/catalyst",
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
}}
"""

    def _get_mock_analysis(self, horizon: str, context_data: Dict[str, Any]) -> LLMAnalysisOutput:
        # A live-data failure must never be disguised as a confident model view.
        if not settings.MOCK_MODE:
            return LLMAnalysisOutput(
                bias="NEUTRAL", strength="WEAK",
                main_driver="Live market context was collected, but the AI synthesis is temporarily unavailable.",
                supporting_factors=[], conflicting_factors=["No validated AI synthesis available"],
                base_scenario="No confident directional scenario is issued until the synthesis service recovers.",
                alternative_scenario="Wait for the next verified macro release or market-data refresh.",
                invalidation="Not applicable while the analysis is unavailable.",
                key_risks=["Free-model availability or rate limit"],
                next_catalyst="Next scheduled macroeconomic release", risk_level="HIGH"
            )
        if horizon == "MONTH":
            return LLMAnalysisOutput(
                bias="BULLISH",
                strength="STRONG",
                main_driver="Structural central bank gold purchases combined with anticipated Federal Reserve rate cutting cycle.",
                supporting_factors=[
                    "Record central bank net official gold reserve acquisitions",
                    "Deceleration in US CPI inflation supporting real yield decline",
                    "De-dollarization trend and institutional ETF net inflows"
                ],
                conflicting_factors=[
                    "Resilient US GDP growth and labor market tightness preventing rapid rate cuts"
                ],
                base_scenario="Gold fundamental backdrop remains structurally bullish supported by lower US real yield expectations and steady central bank accumulation.",
                alternative_scenario="A sharp upside re-acceleration in US core inflation forcing the Fed to pause or raise rate projections would weaken Gold fundamentals.",
                invalidation="Sustained hawkish repricing pushing US 10Y TIPS real yields above 2.25% with renewed DXY strength.",
                key_risks=["Unexpected hawkish Fed policy pivot", "Surge in nominal Treasury yields"],
                next_catalyst="Upcoming FOMC Rate Decision and Staff Macroeconomic Projections",
                risk_level="MEDIUM"
            )
        elif horizon == "WEEK":
            return LLMAnalysisOutput(
                bias="BULLISH",
                strength="MODERATE",
                main_driver="Dovish commentary from Fed leadership easing 10Y real yields.",
                supporting_factors=[
                    "US Core CPI cooler than consensus expectations",
                    "Modest weakening in DXY index below 104.00"
                ],
                conflicting_factors=[
                    "US jobless claims remain historically low"
                ],
                base_scenario="Gold trades with positive fundamental tilt as rate cut expectations solidify.",
                alternative_scenario="Stronger US retail sales and PMI data dampening immediate rate-cut urgency.",
                invalidation="Upside surprise in US PPI or Core PCE data.",
                key_risks=["Fed speaker pushback against aggressive easing"],
                next_catalyst="US Non-Farm Payrolls (NFP) report",
                risk_level="MEDIUM"
            )
        elif horizon == "DAY":
            return LLMAnalysisOutput(
                bias="NEUTRAL",
                strength="MODERATE",
                main_driver="Market digesting softer US inflation data ahead of upcoming Fed comments.",
                supporting_factors=[
                    "Real yield easing following CPI release",
                    "Safe-haven bid supported by Middle East tension"
                ],
                conflicting_factors=[
                    "Equities rally reducing immediate safe-haven allocations"
                ],
                base_scenario="Consolidation in fundamental sentiment prior to US session catalysts.",
                alternative_scenario="Hawkish comments from afternoon Fed speaker triggering yields rebound.",
                invalidation="US Dollar Index surging above recent high.",
                key_risks=["Intraday Fed comments"],
                next_catalyst="Fed Chair Powell speech",
                risk_level="LOW"
            )
        else: # SESSION
            return LLMAnalysisOutput(
                bias="BULLISH",
                strength="MODERATE",
                main_driver="Intraday softness in US Treasury yields following European market open.",
                supporting_factors=[
                    "Euros strengthening vs USD",
                    "Subdued 10Y real yield in Asian session"
                ],
                conflicting_factors=[
                    "Intraday profit taking in commodity basket"
                ],
                base_scenario="Current session fundamentals favor Gold upside.",
                alternative_scenario="Surge in US yields at Wall Street open.",
                invalidation="Breach of overnight USD lows.",
                key_risks=["US session economic releases"],
                next_catalyst="US Wall Street Market Open & Economic Releases",
                risk_level="LOW"
            )
