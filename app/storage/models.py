import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class APISpecModel(Base):
    __tablename__ = "api_specs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    base_url = Column(String(500), nullable=True)
    raw_content = Column(Text, nullable=False)
    format = Column(String(10), nullable=False) # json or yaml
    endpoints_count = Column(Integer, default=0)
    parsed_metadata = Column(JSON, nullable=True) # Full parsed endpoints structure
    created_at = Column(DateTime, default=datetime.utcnow)

    risk_analyses = relationship("RiskAnalysisModel", back_populates="spec", cascade="all, delete-orphan")
    test_cases = relationship("TestCaseModel", back_populates="spec", cascade="all, delete-orphan")
    execution_runs = relationship("ExecutionRunModel", back_populates="spec", cascade="all, delete-orphan")


class RiskAnalysisModel(Base):
    __tablename__ = "risk_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    spec_id = Column(String(36), ForeignKey("api_specs.id"), nullable=False)
    overall_risk = Column(String(20), nullable=False) # HIGH, MEDIUM, LOW
    risk_score = Column(Float, default=0.0) # 0-100 score
    summary = Column(Text, nullable=True)
    endpoint_risks = Column(JSON, nullable=False) # List of dicts per endpoint
    created_at = Column(DateTime, default=datetime.utcnow)

    spec = relationship("APISpecModel", back_populates="risk_analyses")


class TestCaseModel(Base):
    __tablename__ = "test_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    spec_id = Column(String(36), ForeignKey("api_specs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False) # Functional, Boundary, Negative, Security, Authorization, Invalid payload, Missing fields, Large payload, Unexpected types
    priority = Column(String(20), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    objective = Column(Text, nullable=False)
    headers = Column(JSON, nullable=True)
    params = Column(JSON, nullable=True)
    body = Column(JSON, nullable=True)
    expected_status = Column(Integer, nullable=False)
    expected_result = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    spec = relationship("APISpecModel", back_populates="test_cases")
    results = relationship("TestResultModel", back_populates="test_case", cascade="all, delete-orphan")


class ExecutionRunModel(Base):
    __tablename__ = "execution_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    spec_id = Column(String(36), ForeignKey("api_specs.id"), nullable=False)
    target_url = Column(String(500), nullable=False)
    status = Column(String(20), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    warning_tests = Column(Integer, default=0)
    pass_rate = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    total_duration_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    spec = relationship("APISpecModel", back_populates="execution_runs")
    results = relationship("TestResultModel", back_populates="execution_run", cascade="all, delete-orphan")


class TestResultModel(Base):
    __tablename__ = "test_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_run_id = Column(String(36), ForeignKey("execution_runs.id"), nullable=False)
    test_case_id = Column(String(36), ForeignKey("test_cases.id"), nullable=False)
    status = Column(String(20), nullable=False) # PASS, FAIL, WARNING, ERROR
    status_code = Column(Integer, nullable=True)
    latency_ms = Column(Float, default=0.0)
    request_url = Column(String(500), nullable=True)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)
    expected_summary = Column(Text, nullable=True)
    actual_summary = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)

    execution_run = relationship("ExecutionRunModel", back_populates="results")
    test_case = relationship("TestCaseModel", back_populates="results")
    ai_defect_analysis = relationship("AIDefectAnalysisModel", back_populates="test_result", uselist=False, cascade="all, delete-orphan")


class AIDefectAnalysisModel(Base):
    __tablename__ = "ai_defect_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_result_id = Column(String(36), ForeignKey("test_results.id"), nullable=False)
    is_defect = Column(Boolean, default=True)
    confidence = Column(String(20), nullable=False) # HIGH, MEDIUM, LOW
    possible_defect = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_result = relationship("TestResultModel", back_populates="ai_defect_analysis")
