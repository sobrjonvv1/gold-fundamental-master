from typing import Optional
import redis.asyncio as redis
from app.core.config import settings

redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
        )
    return redis_client


async def close_redis():
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


async def check_redis_connection() -> tuple[bool, str]:
    try:
        client = await get_redis()
        await client.ping()
        return True, "ONLINE"
    except Exception as exc:
        return False, f"OFFLINE: {type(exc).__name__}"
