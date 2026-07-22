from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.storage.models import TestCaseModel
from app.storage.repository import APIRepository
from app.api.v1.schemas import TestCaseResponse
from app.agent.qa_agent import qa_agent

router = APIRouter(prefix="/test-cases", tags=["Test Case Generator"])

@router.post("/generate/{spec_id}", response_model=List[TestCaseResponse])
def generate_test_cases(spec_id: str, db: Session = Depends(get_db)):
    repo = APIRepository(db)
    spec = repo.get_spec(spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="API Specification not found")

    parsed_metadata = spec.parsed_metadata or {}
    raw_cases = qa_agent.generate_test_suite(parsed_metadata)

    # Clean existing test cases for spec
    repo.delete_test_cases_for_spec(spec_id)

    db_cases = []
    for rc in raw_cases:
        tc = TestCaseModel(
            spec_id=spec_id,
            title=rc.get("title", "Test Case"),
            category=rc.get("category", "Functional"),
            priority=rc.get("priority", "MEDIUM"),
            endpoint=rc.get("endpoint", ""),
            method=rc.get("method", "GET"),
            objective=rc.get("objective", ""),
            headers=rc.get("headers"),
            params=rc.get("params"),
            body=rc.get("body"),
            expected_status=rc.get("expected_status", 200),
            expected_result=rc.get("expected_result", ""),
            is_active=True
        )
        db_cases.append(tc)

    saved_cases = repo.save_test_cases(db_cases)
    return saved_cases

@router.get("/{spec_id}", response_model=List[TestCaseResponse])
def get_test_cases(
    spec_id: str,
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    repo = APIRepository(db)
    cases = repo.get_test_cases(spec_id)
    if not cases:
        # Generate automatically if none exist yet
        cases = generate_test_cases(spec_id, db)

    if category:
        cases = [c for c in cases if c.category.lower() == category.lower()]
    if priority:
        cases = [c for c in cases if c.priority.lower() == priority.lower()]

    return cases
