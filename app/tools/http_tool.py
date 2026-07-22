from typing import Dict, Any
from app.tools.base import BaseTool
from app.services.test_runner import TestRunner

class ExecuteHTTPRequestTool(BaseTool):
    name = "execute_http_request"
    description = "Executes real HTTP requests against a target REST endpoint with headers, query params, and body payload."

    def execute(self, test_case: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        return TestRunner.execute_test_case(test_case, base_url)
