from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics & Evolution"])

@router.get("")
def get_dashboard_data(db: Session = Depends(get_db)):
    return AnalyticsService.get_dashboard_metrics(db)
