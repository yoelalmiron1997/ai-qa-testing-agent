from typing import List, Optional
from sqlalchemy.orm import Session
from app.storage.models import (
    APISpecModel, RiskAnalysisModel, TestCaseModel,
    ExecutionRunModel, TestResultModel, AIDefectAnalysisModel
)

class APIRepository:
    def __init__(self, db: Session):
        self.db = db

    # APISpec
    def save_spec(self, spec: APISpecModel) -> APISpecModel:
        self.db.add(spec)
        self.db.commit()
        self.db.refresh(spec)
        return spec

    def get_spec(self, spec_id: str) -> Optional[APISpecModel]:
        return self.db.query(APISpecModel).filter(APISpecModel.id == spec_id).first()

    def list_specs(self) -> List[APISpecModel]:
        return self.db.query(APISpecModel).order_by(APISpecModel.created_at.desc()).all()

    def delete_spec(self, spec_id: str) -> bool:
        spec = self.get_spec(spec_id)
        if spec:
            self.db.delete(spec)
            self.db.commit()
            return True
        return False

    # Risk Analysis
    def save_risk_analysis(self, risk: RiskAnalysisModel) -> RiskAnalysisModel:
        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def get_latest_risk_analysis(self, spec_id: str) -> Optional[RiskAnalysisModel]:
        return (
            self.db.query(RiskAnalysisModel)
            .filter(RiskAnalysisModel.spec_id == spec_id)
            .order_by(RiskAnalysisModel.created_at.desc())
            .first()
        )

    # Test Cases
    def save_test_cases(self, test_cases: List[TestCaseModel]) -> List[TestCaseModel]:
        self.db.add_all(test_cases)
        self.db.commit()
        for tc in test_cases:
            self.db.refresh(tc)
        return test_cases

    def get_test_cases(self, spec_id: str) -> List[TestCaseModel]:
        return (
            self.db.query(TestCaseModel)
            .filter(TestCaseModel.spec_id == spec_id, TestCaseModel.is_active == True)
            .all()
        )

    def delete_test_cases_for_spec(self, spec_id: str):
        self.db.query(TestCaseModel).filter(TestCaseModel.spec_id == spec_id).delete()
        self.db.commit()

    # Execution Runs
    def save_execution_run(self, run: ExecutionRunModel) -> ExecutionRunModel:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_execution_run(self, run_id: str) -> Optional[ExecutionRunModel]:
        return self.db.query(ExecutionRunModel).filter(ExecutionRunModel.id == run_id).first()

    def list_execution_runs(self, spec_id: Optional[str] = None) -> List[ExecutionRunModel]:
        query = self.db.query(ExecutionRunModel)
        if spec_id:
            query = query.filter(ExecutionRunModel.spec_id == spec_id)
        return query.order_by(ExecutionRunModel.created_at.desc()).all()

    # Test Results
    def save_test_result(self, result: TestResultModel) -> TestResultModel:
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_test_results(self, run_id: str) -> List[TestResultModel]:
        return (
            self.db.query(TestResultModel)
            .filter(TestResultModel.execution_run_id == run_id)
            .all()
        )

    # AI Defect Analysis
    def save_ai_defect_analysis(self, analysis: AIDefectAnalysisModel) -> AIDefectAnalysisModel:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_ai_defect_analysis(self, result_id: str) -> Optional[AIDefectAnalysisModel]:
        return (
            self.db.query(AIDefectAnalysisModel)
            .filter(AIDefectAnalysisModel.test_result_id == result_id)
            .first()
        )
