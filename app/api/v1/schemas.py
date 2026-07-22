from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class APISpecCreate(BaseModel):
    title: Optional[str] = None
    content: str

class APISpecResponse(BaseModel):
    id: str
    title: str
    version: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    format: str
    endpoints_count: int
    created_at: datetime
    parsed_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class RiskAnalysisResponse(BaseModel):
    id: str
    spec_id: str
    overall_risk: str
    risk_score: float
    summary: Optional[str] = None
    endpoint_risks: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

class TestCaseResponse(BaseModel):
    id: str
    spec_id: str
    title: str
    category: str
    priority: str
    endpoint: str
    method: str
    objective: str
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_status: int
    expected_result: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ExecutionRunCreate(BaseModel):
    spec_id: str
    target_url: Optional[str] = None

class TestResultResponse(BaseModel):
    id: str
    execution_run_id: str
    test_case_id: str
    status: str
    status_code: Optional[int] = None
    latency_ms: float
    request_url: Optional[str] = None
    request_headers: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_headers: Optional[Dict[str, Any]] = None
    response_body: Optional[str] = None
    expected_summary: Optional[str] = None
    actual_summary: Optional[str] = None
    error_details: Optional[str] = None
    executed_at: datetime

    class Config:
        from_attributes = True

class ExecutionRunResponse(BaseModel):
    id: str
    spec_id: str
    target_url: str
    status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    pass_rate: float
    avg_latency_ms: float
    total_duration_ms: float
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AIDefectAnalysisResponse(BaseModel):
    id: str
    test_result_id: str
    is_defect: bool
    confidence: str
    possible_defect: str
    reason: str
    recommendation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
