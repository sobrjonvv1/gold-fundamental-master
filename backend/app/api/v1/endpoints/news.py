from fastapi import APIRouter
from app.collectors.mock_provider import MockNewsProvider

router = APIRouter(prefix="/gold", tags=["News Engine"])


@router.get("/news")
async def get_latest_news():
    news_provider = MockNewsProvider()
    items = await news_provider.fetch_latest_news()
    return {
        "count": len(items),
        "news": items
    }
