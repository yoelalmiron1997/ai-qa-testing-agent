import os
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader

class ReportService:
    """
    Evidence & Report Generation Service.
    Produces self-contained Jinja2 HTML reports and Markdown test execution summaries.
    """

    def __init__ (self):
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_html_report(self, run_data: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        template = self.env.get_template("report.html.j2")
        return template.render(
            spec_title=run_data.get("spec_title", "API Test Suite"),
            spec_version=run_data.get("spec_version", "1.0.0"),
            created_at=run_data.get("created_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
            pass_rate=run_data.get("pass_rate", 0.0),
            total_tests=run_data.get("total_tests", 0),
            passed_tests=run_data.get("passed_tests", 0),
            failed_tests=run_data.get("failed_tests", 0),
            avg_latency_ms=run_data.get("avg_latency_ms", 0.0),
            results=results
        )

    def generate_markdown_report(self, run_data: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        lines = [
            f"# AI QA Testing Evidence Report",
            f"**API Specification:** {run_data.get('spec_title', 'API')} (v{run_data.get('spec_version', '1.0.0')})",
            f"**Execution Date:** {run_data.get('created_at', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))}",
            f"**Pass Rate:** {run_data.get('pass_rate', 0.0)}%",
            "",
            "## Summary Metrics",
            f"- **Total Scenarios Run:** {run_data.get('total_tests', 0)}",
            f"- **Passed:** {run_data.get('passed_tests', 0)}",
            f"- **Failed / Defects:** {run_data.get('failed_tests', 0)}",
            f"- **Average Latency:** {run_data.get('avg_latency_ms', 0.0)} ms",
            "",
            "## Detailed Results & AI Evidence",
            ""
        ]

        for res in results:
            status_icon = "✅ PASS" if res.get("status") == "PASS" else "❌ FAIL"
            lines.append(f"### {status_icon}: {res.get('title')}")
            lines.append(f"- **Category:** {res.get('category')}")
            lines.append(f"- **Endpoint:** `{res.get('request_url')}`")
            lines.append(f"- **Status Code:** HTTP {res.get('status_code')}")
            lines.append(f"- **Response Latency:** {res.get('latency_ms')} ms")
            lines.append("")
            lines.append("```json")
            lines.append(str(res.get("response_body", "")))
            lines.append("```")

            defect = res.get("defect")
            if defect:
                lines.append(f"> **AI Defect Analysis ({defect.get('confidence')} Confidence):**")
                lines.append(f"> {defect.get('possible_defect')}: {defect.get('reason')}")
                if defect.get("recommendation"):
                    lines.append(f"> *Recommendation:* {defect.get('recommendation')}")
            lines.append("")

        return "\n".join(lines)

report_service = ReportService()
