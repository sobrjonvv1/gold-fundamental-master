"""Telegram polling service managed by the FastAPI lifespan."""

import asyncio
import html
import logging
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.domain import TelegramUser
from app.collectors.live_context import collect_context
from app.engine.fundamental_engine import FundamentalEngine

logger = logging.getLogger("gold_fundamental.telegram")
engine = FundamentalEngine()


@dataclass
class TelegramRuntime:
    state: str = "DISABLED"
    detail: str = "Polling is disabled"


runtime = TelegramRuntime()

LANGUAGES = {"ru": "Русский", "en": "English", "uz": "O'zbek", "tk": "Türkmen"}


def _language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=name, callback_data=f"lang:{code}") for code, name in LANGUAGES.items()
    ]])


async def _set_user_language(user_data: types.User, language: str) -> None:
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(TelegramUser).where(TelegramUser.telegram_id == user_data.id))
        if user is None:
            user = TelegramUser(telegram_id=user_data.id, username=user_data.username, first_name=user_data.first_name, language_code=language)
            session.add(user)
        else:
            user.language_code = language
            user.is_active = True
        await session.commit()


async def _get_user_language(message: types.Message) -> str:
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(TelegramUser).where(TelegramUser.telegram_id == message.from_user.id))
        return user.language_code if user and user.language_code in LANGUAGES else "en"


def _text(language: str, key: str) -> str:
    labels = {
        "ru": {"choose":"Выберите язык сообщений:", "saved":"Язык сохранён. Команды: /today /week /month /session /details /sources /status", "brief":"Краткий фундаментальный статус", "details":"Подробный фундаментальный отчёт", "sources":"Источники", "uncertain":"Неопределённость: вывод не является инвестиционной рекомендацией."},
        "en": {"choose":"Choose your report language:", "saved":"Language saved. Commands: /today /week /month /session /details /sources /status", "brief":"Brief fundamental status", "details":"Detailed fundamental report", "sources":"Sources", "uncertain":"Uncertainty: this is not investment advice."},
        "uz": {"choose":"Hisobot tilini tanlang:", "saved":"Til saqlandi. Buyruqlar: /today /week /month /session /details /sources /status", "brief":"Qisqa fundamental holat", "details":"Batafsil fundamental hisobot", "sources":"Manbalar", "uncertain":"Noaniqlik: bu investitsiya maslahati emas."},
        "tk": {"choose":"Hasabat dilini saýlaň:", "saved":"Dil saklandy. Buýruklar: /today /week /month /session /details /sources /status", "brief":"Gysga fundamental ýagdaý", "details":"Giňişleýin fundamental hasabat", "sources":"Çeşmeler", "uncertain":"Näbellilik: bu maýa goýum maslahaty däl."},
    }
    return labels.get(language, labels["en"])[key]


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


def _format_brief(language: str, title: str, report: dict, quality: str) -> str:
    return (
        f"<b>{_escape(_text(language, 'brief'))}: {_escape(title)}</b>\n\n"
        f"<b>Bias:</b> {_escape(report.get('bias'))} · <b>Strength:</b> {_escape(report.get('strength'))}\n"
        f"<b>Market character:</b> {_escape(report.get('main_driver'))}\n"
        f"<b>Next catalyst:</b> {_escape(report.get('next_catalyst'))}\n"
        f"<b>Data:</b> {_escape(quality)}\n\n<i>{_escape(_text(language, 'uncertain'))}</i>"
    )


async def _build_report(horizon: str) -> tuple[dict, str, list[dict]]:
    events, fed_events, market_obs, news, quality, sources = await collect_context()
    return await engine.analyze_horizon(horizon, events, fed_events, market_obs, news), quality, sources


def _register_handlers(dispatcher: Dispatcher) -> None:
    @dispatcher.message(CommandStart())
    async def start(message: types.Message) -> None:
        await message.answer("<b>GOLD FUNDAMENTAL MASTER</b>\n\n" + _text("en", "choose"), parse_mode=ParseMode.HTML, reply_markup=_language_keyboard())

    @dispatcher.callback_query(lambda c: c.data and c.data.startswith("lang:"))
    async def language_selected(callback: types.CallbackQuery) -> None:
        language = callback.data.split(":", 1)[1]
        if language not in LANGUAGES or not callback.message:
            await callback.answer("Unsupported language")
            return
        await _set_user_language(callback.from_user, language)
        await callback.message.edit_text("<b>GOLD FUNDAMENTAL MASTER</b>\n\n" + _text(language, "saved"), parse_mode=ParseMode.HTML, reply_markup=_mini_app_keyboard())
        await callback.answer()

    async def send_horizon(message: types.Message, horizon: str, title: str) -> None:
        try:
            language = await _get_user_language(message)
            report, quality, _ = await _build_report(horizon)
            await message.answer(
                _format_brief(language, title, report, quality),
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

    @dispatcher.message(Command("details"))
    async def details(message: types.Message) -> None:
        try:
            report, quality, _ = await _build_report("DAY")
            await message.answer(_format_report("DETAILED FUNDAMENTAL", report) + f"\n\n<i>Data quality: {quality}. {_text(await _get_user_language(message), 'uncertain')}</i>", parse_mode=ParseMode.HTML, reply_markup=_mini_app_keyboard())
        except Exception:
            logger.exception("Unable to generate detailed Telegram report")
            await message.answer("❌ The analysis service is temporarily unavailable. Please try again.")

    @dispatcher.message(Command("sources"))
    async def sources(message: types.Message) -> None:
        _, _, sources = await _build_report("DAY")
        items = sources or [{"name":"Demo mode", "status":"MOCK"}]
        await message.answer("<b>Sources</b>\n" + "\n".join(f"• {_escape(x['name'])}: {_escape(x['status'])}" for x in items), parse_mode=ParseMode.HTML)

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


async def broadcast_session_report(session_name: str) -> None:
    """Send one short, fact-based report to opted-in users at session open."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    try:
        report, quality, _ = await _build_report(f"SESSION_{session_name}")
        async with AsyncSessionLocal() as session:
            users = (await session.scalars(select(TelegramUser).where(TelegramUser.is_active.is_(True)))).all()
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        try:
            for user in users:
                try:
                    await bot.send_message(user.telegram_id, _format_brief(user.language_code, f"{session_name} SESSION", report, quality), parse_mode=ParseMode.HTML)
                except Exception:
                    logger.warning("Unable to deliver scheduled report to telegram_id=%s", user.telegram_id)
        finally:
            await bot.session.close()
    except Exception:
        logger.exception("Scheduled %s report failed", session_name)
