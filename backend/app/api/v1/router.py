from fastapi import APIRouter
from app.api.v1.endpoints import gold, calendar, news, admin

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(gold.router)
api_router.include_router(calendar.router)
api_router.include_router(news.router)
api_router.include_router(admin.router)
