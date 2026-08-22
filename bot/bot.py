import asyncio
import logging
import os
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gold_fundamental_bot")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "https://your-domain.com")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_mini_app_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏛 Open Wall Street Terminal", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    text = (
        "<b>GOLD FUNDAMENTAL MASTER</b>\n"
        "<i>Institutional Fundamental Analysis Platform for XAU/USD</i>\n\n"
        "Welcome! This bot provides pure fundamental macro analysis for Gold across 4 horizons:\n"
        "• <b>MONTH</b>: Macro regime, Real Yields, Fed stance\n"
        "• <b>WEEK</b>: Weekly catalysts & Fed speakers\n"
        "• <b>DAY</b>: Today's economic calendar & surprise index\n"
        "• <b>SESSION</b>: Asia, London & New York session drivers\n\n"
        "<b>Commands:</b>\n"
        "/today - Daily Fundamental View\n"
        "/week - Weekly Fundamental View\n"
        "/month - Monthly Fundamental View\n"
        "/session - Session View (Asia/London/NY)\n"
        "/news - Fundamental News & AI Impact\n"
        "/status - System & Data Health Status\n"
        "/history - Fundamental Regime Change History"
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_mini_app_keyboard())


@dp.message(Command("today"))
async def cmd_today(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/api/v1/gold/day", timeout=10.0)
            data = resp.json()
            report = (
                f"<b>GOLD — DAILY FUNDAMENTAL</b>\n\n"
                f"<b>Bias:</b> {data.get('bias')}\n"
                f"<b>Strength:</b> {data.get('strength')}\n\n"
                f"<b>Main Driver:</b>\n{data.get('main_driver')}\n\n"
                f"<b>Supporting Factors:</b>\n" + "\n".join([f"• {f}" for f in data.get('supporting_factors', [])]) + "\n\n"
                f"<b>Conflicting Factors:</b>\n" + "\n".join([f"• {f}" for f in data.get('conflicting_factors', [])]) + "\n\n"
                f"<b>Next Catalyst:</b> {data.get('next_catalyst')}\n\n"
                f"<b>Base Scenario:</b>\n{data.get('base_scenario')}\n\n"
                f"<b>Invalidation:</b>\n{data.get('invalidation')}\n\n"
                f"<i>Data Quality: {data.get('data_quality', 'GOOD')}</i>"
            )
            await message.answer(report, parse_mode=ParseMode.HTML, reply_markup=get_mini_app_keyboard())
        except Exception as e:
            await message.answer(f"❌ Error fetching daily fundamental view: {str(e)}")


@dp.message(Command("week"))
async def cmd_week(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/api/v1/gold/week", timeout=10.0)
            data = resp.json()
            report = f"<b>GOLD — WEEKLY FUNDAMENTAL</b>\n\n<b>Bias:</b> {data.get('bias')}\n<b>Strength:</b> {data.get('strength')}\n\n<b>Main Driver:</b> {data.get('main_driver')}"
            await message.answer(report, parse_mode=ParseMode.HTML, reply_markup=get_mini_app_keyboard())
        except Exception as e:
            await message.answer("❌ Error fetching weekly view.")


@dp.message(Command("month"))
async def cmd_month(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/api/v1/gold/month", timeout=10.0)
            data = resp.json()
            report = f"<b>GOLD — MONTHLY FUNDAMENTAL</b>\n\n<b>Bias:</b> {data.get('bias')}\n<b>Strength:</b> {data.get('strength')}\n\n<b>Main Driver:</b> {data.get('main_driver')}"
            await message.answer(report, parse_mode=ParseMode.HTML, reply_markup=get_mini_app_keyboard())
        except Exception as e:
            await message.answer("❌ Error fetching monthly view.")


@dp.message(Command("session"))
async def cmd_session(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/api/v1/gold/session?name=LONDON", timeout=10.0)
            data = resp.json()
            report = f"<b>GOLD — SESSION FUNDAMENTAL (LONDON)</b>\n\n<b>Bias:</b> {data.get('bias')}\n<b>Strength:</b> {data.get('strength')}\n\n<b>Main Driver:</b> {data.get('main_driver')}"
            await message.answer(report, parse_mode=ParseMode.HTML, reply_markup=get_mini_app_keyboard())
        except Exception as e:
            await message.answer("❌ Error fetching session view.")


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BACKEND_URL}/api/v1/system/status", timeout=5.0)
            data = resp.json()
            status_text = (
                f"<b>SYSTEM STATUS</b>\n\n"
                f"Overall: <b>{data.get('status')}</b>\n"
                f"Mock Mode: <code>{data.get('mock_mode')}</code>\n\n"
                f"DATA: {data['components']['DATA']}\n"
                f"AI: {data['components']['AI']}\n"
                f"TELEGRAM: {data['components']['TELEGRAM']}\n"
                f"DATABASE: {data['components']['DATABASE']}\n"
                f"REDIS: {data['components']['REDIS']}"
            )
            await message.answer(status_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            await message.answer("❌ Backend unavailable.")


async def main():
    logger.info("Starting Telegram Bot worker...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
