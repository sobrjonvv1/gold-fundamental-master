"""Telegram polling service managed by the FastAPI lifespan."""

import asyncio
import html
import logging
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.core.config import settings
from app.engine.fundamental_engine import FundamentalEngine

logger = logging.getLogger("gold_fundamental.telegram")
engine = FundamentalEngine()


@dataclass
class TelegramRuntime:
    state: str = "DISABLED"
    detail: str = "Polling is disabled"


runtime = TelegramRuntime()


def status_snapshot() -> dict[str, str]:
    return {"status": runtime.state, "detail": runtime.detail}


def _escape(value: object) -> str:
    return html.escape(str(value), quote=False)


def _mini_app_keyboard() -> InlineKeyboardMarkup | None:
    url = settings.TELEGRAM_WEBAPP_URL
    if not url or not url.startswith("https://"):
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🏛 Open Wall Street Terminal",
                web_app=WebAppInfo(url=url),
            )
        ]]
    )


def _format_report(title: str, report: dict) -> str:
    factors = "\n".join(f"• {_escape(item)}" for item in report.get("supporting_factors", []))
    conflicts = "\n".join(f"• {_escape(item)}" for item in report.get("conflicting_factors", []))
    return (
        f"<b>GOLD — {_escape(title)}</b>\n\n"
        f"<b>Bias:</b> {_escape(report.get('bias', 'N/A'))}\n"
        f"<b>Strength:</b> {_escape(report.get('strength', 'N/A'))}\n\n"
        f"<b>Main Driver:</b>\n{_escape(report.get('main_driver', 'N/A'))}\n\n"
        f"<b>Supporting Factors:</b>\n{factors or '• N/A'}\n\n"
        f"<b>Conflicting Factors:</b>\n{conflicts or '• N/A'}\n\n"
        f"<b>Next Catalyst:</b> {_escape(report.get('next_catalyst', 'N/A'))}\n\n"
        f"<b>Base Scenario:</b>\n{_escape(report.get('base_scenario', 'N/A'))}\n\n"
        f"<b>Invalidation:</b>\n{_escape(report.get('invalidation', 'N/A'))}\n\n"
        f"<i>Data Quality: {_escape(report.get('data_quality', 'UNKNOWN'))}</i>"
    )


def _register_handlers(dispatcher: Dispatcher) -> None:
    @dispatcher.message(CommandStart())
    async def start(message: types.Message) -> None:
        text = (
            "<b>GOLD FUNDAMENTAL MASTER</b>\n"
            "<i>Fundamental analysis platform for XAU/USD</i>\n\n"
            "Commands:\n"
            "/today — daily view\n/week — weekly view\n/month — monthly view\n"
            "/session — London session\n/news — latest news\n"
            "/history — state history\n/status — service status"
        )
        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=_mini_app_keyboard())

    async def send_horizon(message: types.Message, horizon: str, title: str) -> None:
        try:
            report = await engine.analyze_horizon(horizon, [], [], {}, [])
            await message.answer(
                _format_report(title, report),
                parse_mode=ParseMode.HTML,
                reply_markup=_mini_app_keyboard(),
            )
        except Exception:
            logger.exception("Unable to generate %s Telegram report", horizon)
            await message.answer("❌ The analysis service is temporarily unavailable. Please try again.")

    @dispatcher.message(Command("today"))
    async def today(message: types.Message) -> None:
        await send_horizon(message, "DAY", "DAILY FUNDAMENTAL")

    @dispatcher.message(Command("week"))
    async def week(message: types.Message) -> None:
        await send_horizon(message, "WEEK", "WEEKLY FUNDAMENTAL")

    @dispatcher.message(Command("month"))
    async def month(message: types.Message) -> None:
        await send_horizon(message, "MONTH", "MONTHLY FUNDAMENTAL")

    @dispatcher.message(Command("session"))
    async def session(message: types.Message) -> None:
        await send_horizon(message, "SESSION_LONDON", "LONDON SESSION FUNDAMENTAL")

    @dispatcher.message(Command("news"))
    async def news(message: types.Message) -> None:
        await message.answer("News feed is not configured yet. Current mode: " + ("MOCK" if settings.MOCK_MODE else "LIVE"))

    @dispatcher.message(Command("history"))
    async def history(message: types.Message) -> None:
        await message.answer("History storage will be available after the first scheduled analysis cycle.")

    @dispatcher.message(Command("status"))
    async def status(message: types.Message) -> None:
        from app.api.v1.endpoints.system import collect_system_status

        data = await collect_system_status()
        components = data["components"]
        text = (
            "<b>SYSTEM STATUS</b>\n\n"
            f"Overall: <b>{_escape(data['status'])}</b>\n"
            f"Mode: <code>{'MOCK' if data['mock_mode'] else 'LIVE'}</code>\n\n"
            + "\n".join(f"{_escape(name)}: {_escape(value)}" for name, value in components.items())
        )
        await message.answer(text, parse_mode=ParseMode.HTML)


async def run_telegram_bot() -> None:
    """Poll Telegram forever, recovering from transient network/API failures."""
    if not settings.TELEGRAM_BOT_TOKEN:
        runtime.state, runtime.detail = "DISABLED", "TELEGRAM_BOT_TOKEN is not configured"
        logger.warning(runtime.detail)
        return

    delay = 1
    while True:
        bot: Bot | None = None
        try:
            runtime.state, runtime.detail = "STARTING", "Connecting to Telegram"
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            dispatcher = Dispatcher()
            _register_handlers(dispatcher)
            await bot.delete_webhook(drop_pending_updates=False)
            runtime.state, runtime.detail = "ONLINE", "Polling Telegram updates"
            delay = 1
            await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
        except asyncio.CancelledError:
            runtime.state, runtime.detail = "STOPPED", "Shutdown requested"
            raise
        except Exception as exc:
            runtime.state, runtime.detail = "OFFLINE", type(exc).__name__
            logger.exception("Telegram polling failed; retrying in %ss", delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, settings.TELEGRAM_RESTART_MAX_DELAY_SECONDS)
        finally:
            if bot is not None:
                await bot.session.close()
