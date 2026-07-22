from typing import Dict, Any, List
from app.tools.base import BaseTool
from app.services.report_service import report_service

class GenerateReportTool(BaseTool):
    name = "generate_report"
    description = "Generates HTML or Markdown evidence reports from test execution data."

    def execute(self, run_data: Dict[str, Any], results: List[Dict[str, Any]], format_type: str = "html") -> str:
        if format_type.lower() == "markdown":
            return report_service.generate_markdown_report(run_data, results)
        return report_service.generate_html_report(run_data, results)
