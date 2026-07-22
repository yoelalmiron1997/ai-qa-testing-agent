from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.storage.repository import APIRepository
from app.api.v1.schemas import AIDefectAnalysisResponse

router = APIRouter(prefix="/ai-analysis", tags=["AI Defect Diagnostic"])

@router.get("/result/{result_id}", response_model=AIDefectAnalysisResponse)
def get_ai_defect_analysis(result_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    analysis = repo.get_ai_defect_analysis(result_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="No AI defect analysis found for this test result")
    return analysis
