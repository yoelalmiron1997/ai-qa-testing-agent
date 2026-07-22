import json
from typing import Dict, Any, Optional
from app.core.llm import llm_client

class DefectAnalyzer:
    """
    AI QA Defect Diagnostic & Root Cause Analysis Engine.
    Analyzes execution results against expected outcomes to detect defects,
    assign confidence scores, explain failure reasoning, and suggest remediation steps.
    """

    @staticmethod
    def analyze_result(test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        status = result.get("status")
        status_code = result.get("status_code", 0)
        expected_status = test_case.get("expected_status")
        response_body = result.get("response_body", "")
        error_details = result.get("error_details", "")
        category = test_case.get("category", "")
        endpoint = test_case.get("endpoint", "")
        method = test_case.get("method", "")

        # If test passed clean, return no defect detected
        if status == "PASS":
            return {
                "is_defect": False,
                "confidence": "HIGH",
                "possible_defect": "None",
                "reason": f"Endpoint responded with expected status HTTP {status_code}.",
                "recommendation": "No action required. Test passed successfully."
            }

        # Deterministic analysis for fallback
        possible_defect = "Unexpected HTTP Response Behavior"
        confidence = "HIGH"
        reason = ""
        recommendation = ""

        if status_code == 500:
            possible_defect = "Unhandled Internal Server Error (HTTP 500)"
            confidence = "HIGH"
            reason = f"Endpoint {method} {endpoint} returned HTTP 500 Internal Server Error instead of expected HTTP {expected_status}. This indicates an unhandled exception or crash in backend service logic."
            recommendation = "Inspect backend application error logs and wrap payload/input validation in explicit try-catch error handlers returning HTTP 400 or 404."
        elif status_code == 404 and expected_status != 404:
            possible_defect = "Endpoint Routing or Resource Not Found"
            confidence = "HIGH"
            reason = f"Requested URI {endpoint} returned HTTP 404 Not Found, but expected HTTP {expected_status}."
            recommendation = "Verify endpoint route mapping and database seed data for path resources."
        elif status_code == 401 or status_code == 403:
            possible_defect = "Authentication / Access Enforcement Rejection"
            confidence = "MEDIUM"
            reason = f"Endpoint rejected execution with HTTP {status_code}. Expected status was HTTP {expected_status}."
            recommendation = "Verify API key, bearer tokens, and security permissions configured for the test execution run."
        elif status == "ERROR":
            possible_defect = "Network Connectivity or Service Unreachable"
            confidence = "HIGH"
            reason = f"HTTP request failed to execute: {error_details}."
            recommendation = "Ensure the target API server is running and accessible at the designated host/port."
        else:
            possible_defect = f"Status Code Mismatch (Expected {expected_status}, Got {status_code})"
            confidence = "HIGH"
            reason = f"Endpoint returned HTTP {status_code} when HTTP {expected_status} was expected for category '{category}'."
            recommendation = f"Update API implementation or update specification expectations if status {status_code} is intended."

        fallback_analysis = {
            "is_defect": True,
            "confidence": confidence,
            "possible_defect": possible_defect,
            "reason": reason,
            "recommendation": recommendation
        }

        # Optional LLM refinement for rich insights
        system_prompt = """You are a Senior Principal AI QA Engineer. Analyze the executed REST API test failure and return a structured JSON analysis."""
        user_prompt = f"""
Test Title: {test_case.get('title')}
Endpoint: {method} {endpoint}
Test Category: {category}
Expected Status: {expected_status}
Actual Status Code: {status_code}
Error Details: {error_details}
Response Snippet: {response_body[:500]}
"""

        return llm_client.generate_json(system_prompt, user_prompt, fallback_analysis)
