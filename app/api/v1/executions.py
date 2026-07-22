import time
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.storage.models import ExecutionRunModel, TestResultModel, AIDefectAnalysisModel
from app.storage.repository import APIRepository
from app.api.v1.schemas import ExecutionRunCreate, ExecutionRunResponse, TestResultResponse
from app.agent.qa_agent import qa_agent

router = APIRouter(prefix="/executions", tags=["Test Execution Engine"])

@router.post("", response_model=ExecutionRunResponse)
def execute_test_suite(payload: ExecutionRunCreate, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    spec = repo.get_spec(payload.spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="API Specification not found")

    test_cases = repo.get_test_cases(payload.spec_id)
    if not test_cases:
        test_cases = qa_agent.generate_test_suite(spec.parsed_metadata or {})

    target_url = payload.target_url or spec.base_url or "http://localhost:8000"

    # Initialize execution run record
    run = ExecutionRunModel(
        spec_id=payload.spec_id,
        target_url=target_url,
        status="RUNNING",
        total_tests=len(test_cases),
        passed_tests=0,
        failed_tests=0,
        warning_tests=0,
        pass_rate=0.0,
        avg_latency_ms=0.0,
        total_duration_ms=0.0
    )
    saved_run = repo.save_execution_run(run)

    start_run_time = time.time()
    passed_cnt = 0
    failed_cnt = 0
    total_latency = 0.0

    for tc in test_cases:
        if isinstance(tc, dict):
            tc_dict = {
                "id": tc.get("id"),
                "title": tc.get("title", "Generated Test Case"),
                "category": tc.get("category", "Functional"),
                "priority": tc.get("priority", "MEDIUM"),
                "endpoint": tc.get("endpoint", "/"),
                "method": tc.get("method", "GET"),
                "headers": tc.get("headers"),
                "params": tc.get("params"),
                "body": tc.get("body"),
                "expected_status": tc.get("expected_status", 200),
                "expected_result": tc.get("expected_result", "200 OK")
            }
            tc_id = tc.get("id")
        else:
            tc_dict = {
                "id": tc.id,
                "title": tc.title,
                "category": tc.category,
                "priority": tc.priority,
                "endpoint": tc.endpoint,
                "method": tc.method,
                "headers": tc.headers,
                "params": tc.params,
                "body": tc.body,
                "expected_status": tc.expected_status,
                "expected_result": tc.expected_result
            }
            tc_id = tc.id

        # Execute HTTP Request
        exec_res = qa_agent.execute_test(tc_dict, target_url)

        status = exec_res.get("status", "FAIL")
        if status == "PASS":
            passed_cnt += 1
        else:
            failed_cnt += 1

        latency = exec_res.get("latency_ms", 0.0)
        total_latency += latency

        # Store test result
        result_model = TestResultModel(
            execution_run_id=saved_run.id,
            test_case_id=tc_id,
            status=status,
            status_code=exec_res.get("status_code"),
            latency_ms=latency,
            request_url=exec_res.get("request_url"),
            request_headers=exec_res.get("request_headers"),
            request_body=exec_res.get("request_body"),
            response_headers=exec_res.get("response_headers"),
            response_body=exec_res.get("response_body"),
            expected_summary=exec_res.get("expected_summary"),
            actual_summary=exec_res.get("actual_summary"),
            error_details=exec_res.get("error_details")
        )
        saved_result = repo.save_test_result(result_model)

        # Trigger AI Defect Analysis for non-PASS results
        if status != "PASS":
            defect_data = qa_agent.diagnose_failure(tc_dict, exec_res)
            defect_model = AIDefectAnalysisModel(
                test_result_id=saved_result.id,
                is_defect=defect_data.get("is_defect", True),
                confidence=defect_data.get("confidence", "HIGH"),
                possible_defect=defect_data.get("possible_defect", "Potential Defect"),
                reason=defect_data.get("reason", "Status mismatch"),
                recommendation=defect_data.get("recommendation")
            )
            repo.save_ai_defect_analysis(defect_model)

    end_run_time = time.time()
    total_duration = round((end_run_time - start_run_time) * 1000, 2)
    avg_latency = round(total_latency / max(len(test_cases), 1), 2)
    pass_rate = round((passed_cnt / max(len(test_cases), 1)) * 100, 1)

    # Update execution run final metrics
    saved_run.status = "COMPLETED"
    saved_run.passed_tests = passed_cnt
    saved_run.failed_tests = failed_cnt
    saved_run.pass_rate = pass_rate
    saved_run.avg_latency_ms = avg_latency
    saved_run.total_duration_ms = total_duration
    saved_run.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(saved_run)

    return saved_run

@router.get("", response_model=List[ExecutionRunResponse])
def list_execution_runs(spec_id: Optional[str] = None, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    return repo.list_execution_runs(spec_id)

@router.get("/{run_id}", response_model=ExecutionRunResponse)
def get_execution_run(run_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    run = repo.get_execution_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Execution run not found")
    return run

@router.get("/{run_id}/results", response_model=List[TestResultResponse])
def get_execution_results(run_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    return repo.get_test_results(run_id)
