from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.storage.repository import APIRepository

class AnalyticsService:
    """
    Quality Analytics & Historical Evolution Service.
    Computes aggregated dashboard metrics, quality trends, and run-over-run evolution.
    """

    @staticmethod
    def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
        repo = APIRepository(db)
        specs = repo.list_specs()
        runs = repo.list_execution_runs()

        total_apis = len(specs)
        total_endpoints = sum(s.endpoints_count for s in specs)
        
        # Calculate total test cases across specs
        total_test_cases = 0
        for s in specs:
            total_test_cases += len(repo.get_test_cases(s.id))

        total_executions = len(runs)
        total_passed = sum(r.passed_tests for r in runs)
        total_failed = sum(r.failed_tests for r in runs)
        total_tests_run = total_passed + total_failed

        overall_pass_rate = round((total_passed / max(total_tests_run, 1)) * 100, 1) if total_tests_run > 0 else 0.0

        # Calculate average latency across runs
        avg_latency = round(sum(r.avg_latency_ms for r in runs) / max(len(runs), 1), 1) if runs else 0.0

        # Evolution trend data (last 10 runs)
        evolution = []
        for r in reversed(runs[:10]):
            evolution.append({
                "id": r.id,
                "created_at": r.created_at.strftime("%m/%d %H:%M"),
                "pass_rate": r.pass_rate,
                "passed": r.passed_tests,
                "failed": r.failed_tests,
                "avg_latency": r.avg_latency_ms
            })

        return {
            "total_apis": total_apis,
            "total_endpoints": total_endpoints,
            "total_test_cases": total_test_cases,
            "total_executions": total_executions,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "overall_pass_rate": overall_pass_rate,
            "avg_latency_ms": avg_latency,
            "evolution": evolution
        }
