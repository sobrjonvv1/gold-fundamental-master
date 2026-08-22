import asyncio
import httpx
import os

token = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def test_bot_info():
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN is not configured.")
        return
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"https://api.telegram.org/bot{token}/getMe")
        if resp.status_code == 200:
            data = resp.json()
            bot_info = data.get("result", {})
            print("SUCCESS: Bot connected to Telegram!")
            print(f"Bot ID: {bot_info.get('id')}")
            print(f"Bot Name: {bot_info.get('first_name')}")
            print(f"Bot Username: @{bot_info.get('username')}")
        else:
            print(f"ERROR: Telegram returned HTTP {resp.status_code}.")


if __name__ == "__main__":
    asyncio.run(test_bot_info())
