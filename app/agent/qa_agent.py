import logging
from typing import Dict, Any, List
from app.agent.prompts import QA_AGENT_SYSTEM_PROMPT
from app.tools.openapi_tool import ReadOpenAPITool
from app.tools.http_tool import ExecuteHTTPRequestTool
from app.tools.schema_tool import CompareSchemaTool
from app.tools.report_tool import GenerateReportTool
from app.services.risk_analyzer import RiskAnalyzer
from app.services.test_generator import TestGenerator
from app.services.defect_analyzer import DefectAnalyzer

logger = logging.getLogger(__name__)

class AIQAAgent:
    """
    Autonomous AI QA Agent.
    Coordinates tools, conducts risk evaluation, plans test suites, executes HTTP calls,
    and analyzes defects with structured reasoning.
    """

    def __init__(self):
        self.read_openapi_tool = ReadOpenAPITool()
        self.http_tool = ExecuteHTTPRequestTool()
        self.schema_tool = CompareSchemaTool()
        self.report_tool = GenerateReportTool()

    def parse_and_inspect_spec(self, content: str, filename: str = "") -> Dict[str, Any]:
        logger.info("AI QA Agent: Reading and inspecting OpenAPI specification...")
        return self.read_openapi_tool.execute(content, filename)

    def analyze_risks(self, spec_metadata: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("AI QA Agent: Evaluating endpoint risk profiles...")
        return RiskAnalyzer.analyze_api_risk(spec_metadata)

    def generate_test_suite(self, spec_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        logger.info("AI QA Agent: Generating prioritized 9-category test suite...")
        return TestGenerator.generate_test_cases_for_spec(spec_metadata)

    def execute_test(self, test_case: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        logger.info(f"AI QA Agent: Executing test -> {test_case.get('title')}")
        result = self.http_tool.execute(test_case, base_url)

        # Validate JSON schema if response body & schema present
        if result.get("response_body") and test_case.get("schema"):
            schema_res = self.schema_tool.execute(result["response_body"], test_case["schema"])
            if not schema_res["is_valid"]:
                result["status"] = "FAIL"
                result["error_details"] = (result.get("error_details") or "") + f" [Schema Error: {schema_res['error']}]"

        return result

    def diagnose_failure(self, test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"AI QA Agent: Diagnosing execution failure for {test_case.get('title')}...")
        return DefectAnalyzer.analyze_result(test_case, result)

    def build_evidence_report(self, run_data: Dict[str, Any], results: List[Dict[str, Any]], format_type: str = "html") -> str:
        logger.info("AI QA Agent: Building quality evidence report...")
        return self.report_tool.execute(run_data, results, format_type)

qa_agent = AIQAAgent()
