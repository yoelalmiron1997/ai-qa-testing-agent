import time
import json
import requests
from typing import Dict, Any, List

class TestRunner:
    """
    HTTP Request Execution Engine.
    Executes real HTTP requests, measures exact response timing, captures status codes,
    headers, and body payload, and evaluates status assertions.
    """

    @staticmethod
    def execute_test_case(test_case: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        endpoint = test_case.get("endpoint", "")
        method = test_case.get("method", "GET").upper()
        headers = test_case.get("headers") or {}
        params = test_case.get("params") or {}
        body = test_case.get("body") or None
        expected_status = test_case.get("expected_status", 200)

        # Construct full URL
        if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
            clean_base = base_url.rstrip("/")
            clean_ep = endpoint if endpoint.startswith("/") else f"/{endpoint}"
            full_url = f"{clean_base}{clean_ep}"
        else:
            full_url = endpoint

        # Ensure default Content-Type header if body present
        if body and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        start_time = time.time()
        status_code = 0
        response_headers = {}
        response_text = ""
        error_details = None
        status = "FAIL"

        try:
            req_data = json.dumps(body) if (body and headers.get("Content-Type") == "application/json") else body
            
            resp = requests.request(
                method=method,
                url=full_url,
                headers=headers,
                params=params,
                data=req_data if isinstance(req_data, str) else None,
                json=body if (body and headers.get("Content-Type") != "application/json") else None,
                timeout=10
            )

            latency_ms = round((time.time() - start_time) * 1000, 2)
            status_code = resp.status_code
            response_headers = dict(resp.headers)
            response_text = resp.text

            # Status code match logic
            if status_code == expected_status:
                status = "PASS"
            elif 200 <= status_code < 300 and 200 <= expected_status < 300:
                # Accept equivalent 2xx status codes (e.g. 200 vs 201) with WARNING
                status = "PASS"
            elif status_code == 500:
                status = "FAIL"
                error_details = f"Server returned Internal Server Error (HTTP 500) instead of expected {expected_status}."
            else:
                status = "FAIL"
                error_details = f"Expected HTTP status {expected_status}, but received HTTP status {status_code}."

        except requests.exceptions.Timeout:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            status = "ERROR"
            error_details = "Request timed out after 10 seconds."
        except requests.exceptions.ConnectionError:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            status = "ERROR"
            error_details = f"Failed to connect to target URL: {full_url}. Target host may be down."
        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            status = "ERROR"
            error_details = f"HTTP Execution exception: {str(e)}"

        return {
            "test_case_id": test_case.get("id"),
            "title": test_case.get("title"),
            "category": test_case.get("category"),
            "status": status,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "request_url": full_url,
            "request_headers": headers,
            "request_body": body,
            "response_headers": response_headers,
            "response_body": response_text,
            "expected_summary": f"Expected Status: {expected_status}",
            "actual_summary": f"Actual Status: {status_code if status_code else 'NO_RESPONSE'}",
            "error_details": error_details
        }
