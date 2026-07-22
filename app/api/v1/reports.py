from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.storage.repository import APIRepository
from app.agent.qa_agent import qa_agent

router = APIRouter(prefix="/reports", tags=["Evidence Reports"])

@router.get("/html/{run_id}", response_class=HTMLResponse)
def get_html_report(run_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    run = repo.get_execution_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Execution run not found")

    spec = repo.get_spec(run.spec_id)
    results = repo.get_test_results(run_id)

    formatted_results = []
    for r in results:
        tc = repo.db.query(repo.db.models.TestCaseModel).filter_by(id=r.test_case_id).first() if hasattr(repo.db, 'models') else None
        defect = repo.get_ai_defect_analysis(r.id)

        defect_dict = None
        if defect:
            defect_dict = {
                "confidence": defect.confidence,
                "possible_defect": defect.possible_defect,
                "reason": defect.reason,
                "recommendation": defect.recommendation
            }

        formatted_results.append({
            "title": r.expected_summary or "Test Case",
            "category": "API Validation",
            "request_url": r.request_url,
            "status": r.status,
            "status_code": r.status_code,
            "latency_ms": r.latency_ms,
            "request_body": r.request_body,
            "response_body": r.response_body,
            "defect": defect_dict
        })

    run_data = {
        "spec_title": spec.title if spec else "API Test Run",
        "spec_version": spec.version if spec else "1.0.0",
        "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "pass_rate": run.pass_rate,
        "total_tests": run.total_tests,
        "passed_tests": run.passed_tests,
        "failed_tests": run.failed_tests,
        "avg_latency_ms": run.avg_latency_ms
    }

    html_content = qa_agent.build_evidence_report(run_data, formatted_results, format_type="html")
    return HTMLResponse(content=html_content)

@router.get("/markdown/{run_id}")
def get_markdown_report(run_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    run = repo.get_execution_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Execution run not found")

    spec = repo.get_spec(run.spec_id)
    results = repo.get_test_results(run_id)

    formatted_results = []
    for r in results:
        defect = repo.get_ai_defect_analysis(r.id)
        defect_dict = None
        if defect:
            defect_dict = {
                "confidence": defect.confidence,
                "possible_defect": defect.possible_defect,
                "reason": defect.reason,
                "recommendation": defect.recommendation
            }

        formatted_results.append({
            "title": r.expected_summary or "Test Case",
            "category": "API Validation",
            "request_url": r.request_url,
            "status": r.status,
            "status_code": r.status_code,
            "latency_ms": r.latency_ms,
            "request_body": r.request_body,
            "response_body": r.response_body,
            "defect": defect_dict
        })

    run_data = {
        "spec_title": spec.title if spec else "API Test Run",
        "spec_version": spec.version if spec else "1.0.0",
        "created_at": run.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "pass_rate": run.pass_rate,
        "total_tests": run.total_tests,
        "passed_tests": run.passed_tests,
        "failed_tests": run.failed_tests,
        "avg_latency_ms": run.avg_latency_ms
    }

    md_content = qa_agent.build_evidence_report(run_data, formatted_results, format_type="markdown")
    return Response(content=md_content, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename=report_{run_id}.md"})
