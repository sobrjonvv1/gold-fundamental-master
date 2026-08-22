from fastapi import APIRouter, Header, HTTPException, Depends
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin & Debug"])


def check_admin_secret(x_admin_secret: str = Header(None)):
    if settings.MOCK_MODE:
        return True
    if x_admin_secret != settings.SECRET_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid admin secret")


@router.post("/run/month")
async def trigger_month_analysis(auth: bool = Depends(check_admin_secret)):
    return {"message": "Triggered MONTH fundamental analysis update"}


@router.post("/run/week")
async def trigger_week_analysis(auth: bool = Depends(check_admin_secret)):
    return {"message": "Triggered WEEK fundamental analysis update"}


@router.post("/run/day")
async def trigger_day_analysis(auth: bool = Depends(check_admin_secret)):
    return {"message": "Triggered DAY fundamental analysis update"}


@router.post("/run/session")
async def trigger_session_analysis(session_name: str = "LONDON", auth: bool = Depends(check_admin_secret)):
    return {"message": f"Triggered SESSION_{session_name.upper()} fundamental analysis update"}
