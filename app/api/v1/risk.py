from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.storage.models import RiskAnalysisModel
from app.storage.repository import APIRepository
from app.api.v1.schemas import RiskAnalysisResponse
from app.agent.qa_agent import qa_agent

router = APIRouter(prefix="/risk-analysis", tags=["Risk Analysis"])

@router.post("/{spec_id}", response_model=RiskAnalysisResponse)
def analyze_risk(spec_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    spec = repo.get_spec(spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="API Specification not found")

    parsed_metadata = spec.parsed_metadata or {}
    analysis_data = qa_agent.analyze_risks(parsed_metadata)

    risk_model = RiskAnalysisModel(
        spec_id=spec_id,
        overall_risk=analysis_data.get("overall_risk", "LOW"),
        risk_score=analysis_data.get("risk_score", 0.0),
        summary=analysis_data.get("summary", ""),
        endpoint_risks=analysis_data.get("endpoint_risks", [])
    )

    saved_risk = repo.save_risk_analysis(risk_model)
    return saved_risk

@router.get("/{spec_id}", response_model=RiskAnalysisResponse)
def get_risk_analysis(spec_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    risk = repo.get_latest_risk_analysis(spec_id)
    if not risk:
        # Trigger risk analysis if not performed yet
        return analyze_risk(spec_id, db)
    return risk
