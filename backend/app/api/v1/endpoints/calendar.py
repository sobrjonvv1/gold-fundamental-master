from fastapi import APIRouter
from app.collectors.forex_factory import ForexFactoryProvider

router = APIRouter(prefix="/gold", tags=["Economic Calendar"])


@router.get("/events")
async def get_economic_events():
    ff = ForexFactoryProvider()
    events = await ff.fetch_events(None, None)
    return {
        "provider": "forex_factory",
        "count": len(events),
        "events": events
    }
