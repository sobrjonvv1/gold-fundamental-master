import hmac
import hashlib
import urllib.parse
from typing import Dict, Any, Optional
from fastapi import HTTPException, Header, Depends
from app.core.config import settings


def verify_telegram_init_data(init_data: str, bot_token: str) -> Dict[str, Any]:
    """
    Validates Telegram WebApp initData string against Telegram HMAC-SHA256 protocol.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    if settings.MOCK_MODE or not bot_token:
        # Allow mock auth in testing or mock mode
        return {"id": 12345678, "first_name": "Demo", "username": "demouser"}

    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        if "hash" not in parsed_data:
            raise ValueError("Missing hash parameter")

        received_hash = parsed_data.pop("hash")
        
        # Sort keys alphabetically
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash != received_hash:
            raise ValueError("Invalid hash signature")

        user_json_str = parsed_data.get("user")
        if user_json_str:
            import json
            return json.loads(user_json_str)
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Telegram authentication failed: {str(e)}")


async def get_current_telegram_user(x_telegram_init_data: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not x_telegram_init_data:
        if settings.MOCK_MODE:
            return {"id": 12345678, "first_name": "MockUser", "username": "mockuser"}
        raise HTTPException(status_code=401, detail="Missing X-Telegram-Init-Data header")
    return verify_telegram_init_data(x_telegram_init_data, settings.TELEGRAM_BOT_TOKEN)
