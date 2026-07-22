import json
from typing import Dict, Any, List

class TestGenerator:
    """
    Automated QA Test Case Scenario Generator.
    Generates structured test cases across 9 testing categories.
    """

    CATEGORIES = [
        "Functional",
        "Boundary",
        "Negative",
        "Security",
        "Authorization",
        "Invalid payload",
        "Missing fields",
        "Large payload",
        "Unexpected types"
    ]

    @staticmethod
    def generate_test_cases_for_spec(spec_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        endpoints = spec_metadata.get("endpoints", [])
        test_cases: List[Dict[str, Any]] = []

        for ep in endpoints:
            ep_cases = TestGenerator.generate_endpoint_test_cases(ep)
            test_cases.extend(ep_cases)

        return test_cases

    @staticmethod
    def generate_endpoint_test_cases(endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        path = endpoint.get("path", "")
        method = endpoint.get("method", "GET").upper()
        parameters = endpoint.get("parameters", [])
        has_auth = endpoint.get("has_auth", False)
        schema = endpoint.get("request_body_schema") or {}

        cases: List[Dict[str, Any]] = []

        # Helper to construct sample valid params/body
        valid_params = {}
        path_params = {}
        for p in parameters:
            p_name = p.get("name")
            p_in = p.get("in")
            p_type = p.get("type", "string")
            sample_val = "1" if p_type in ["integer", "number"] else "test_sample"
            if p_in == "path":
                path_params[p_name] = sample_val
            elif p_in == "query":
                valid_params[p_name] = sample_val

        # Replace path parameters with sample values for execution path
        exec_path = path
        for pk, pv in path_params.items():
            exec_path = exec_path.replace(f"{{{pk}}}", str(pv))

        # Sample valid body
        valid_body = TestGenerator._build_sample_body(schema)

        # 1. Functional (Happy Path)
        cases.append({
            "title": f"Verify {method} {path} - Happy Path",
            "category": "Functional",
            "priority": "CRITICAL",
            "endpoint": exec_path,
            "method": method,
            "objective": f"Validate successful execution of {method} {path} with valid inputs.",
            "headers": {"Content-Type": "application/json"} if valid_body else {},
            "params": valid_params,
            "body": valid_body,
            "expected_status": 200 if method == "GET" else (201 if method == "POST" else 200),
            "expected_result": "Success status code returned with valid response structure."
        })

        # 2. Security (Missing Auth)
        if has_auth:
            cases.append({
                "title": f"Verify {method} {path} - Missing Auth Token",
                "category": "Security",
                "priority": "HIGH",
                "endpoint": exec_path,
                "method": method,
                "objective": "Verify endpoint rejects unauthenticated access.",
                "headers": {},
                "params": valid_params,
                "body": valid_body,
                "expected_status": 401,
                "expected_result": "HTTP 401 Unauthorized status returned."
            })
            
            # 3. Authorization (Invalid Token)
            cases.append({
                "title": f"Verify {method} {path} - Invalid Auth Token",
                "category": "Authorization",
                "priority": "HIGH",
                "endpoint": exec_path,
                "method": method,
                "objective": "Verify endpoint rejects requests with invalid or expired tokens.",
                "headers": {"Authorization": "Bearer invalid_expired_token_12345"},
                "params": valid_params,
                "body": valid_body,
                "expected_status": 401,
                "expected_result": "HTTP 401 Unauthorized status returned."
            })

        # 4. Negative (Non-existent Resource ID)
        if path_params:
            neg_path = path
            for pk in path_params:
                neg_path = neg_path.replace(f"{{{pk}}}", "99999999_non_existent")
            cases.append({
                "title": f"Verify {method} {path} - Non-existent Path Resource",
                "category": "Negative",
                "priority": "HIGH",
                "endpoint": neg_path,
                "method": method,
                "objective": "Verify endpoint handles non-existent resource IDs gracefully.",
                "headers": {},
                "params": valid_params,
                "body": valid_body,
                "expected_status": 404,
                "expected_result": "HTTP 404 Not Found error response returned."
            })

        # Payload tests if body schema exists
        if valid_body and isinstance(valid_body, dict) and len(valid_body) > 0:
            # 5. Invalid Payload (Malformed JSON / empty)
            cases.append({
                "title": f"Verify {method} {path} - Empty Body Payload",
                "category": "Invalid payload",
                "priority": "MEDIUM",
                "endpoint": exec_path,
                "method": method,
                "objective": "Verify endpoint rejects empty JSON payload when body is expected.",
                "headers": {"Content-Type": "application/json"},
                "params": valid_params,
                "body": {},
                "expected_status": 400,
                "expected_result": "HTTP 400 Bad Request error returned."
            })

            # 6. Missing Fields
            missing_body = dict(valid_body)
            first_key = list(missing_body.keys())[0]
            del missing_body[first_key]
            cases.append({
                "title": f"Verify {method} {path} - Missing Field ({first_key})",
                "category": "Missing fields",
                "priority": "HIGH",
                "endpoint": exec_path,
                "method": method,
                "objective": f"Verify endpoint rejects requests missing required field '{first_key}'.",
                "headers": {"Content-Type": "application/json"},
                "params": valid_params,
                "body": missing_body,
                "expected_status": 400,
                "expected_result": "HTTP 400 Bad Request validation error returned."
            })

            # 7. Unexpected Types
            wrong_type_body = dict(valid_body)
            wrong_type_body[first_key] = True # Passing bool instead of string/int
            cases.append({
                "title": f"Verify {method} {path} - Unexpected Field Type ({first_key})",
                "category": "Unexpected types",
                "priority": "MEDIUM",
                "endpoint": exec_path,
                "method": method,
                "objective": f"Verify type checking enforcement on parameter '{first_key}'.",
                "headers": {"Content-Type": "application/json"},
                "params": valid_params,
                "body": wrong_type_body,
                "expected_status": 400,
                "expected_result": "HTTP 400 Bad Request validation error returned."
            })

            # 8. Boundary (Extreme Values)
            boundary_body = dict(valid_body)
            boundary_body[first_key] = "" # Empty string boundary
            cases.append({
                "title": f"Verify {method} {path} - Boundary Empty String ({first_key})",
                "category": "Boundary",
                "priority": "MEDIUM",
                "endpoint": exec_path,
                "method": method,
                "objective": f"Verify boundary check for empty string on field '{first_key}'.",
                "headers": {"Content-Type": "application/json"},
                "params": valid_params,
                "body": boundary_body,
                "expected_status": 400,
                "expected_result": "HTTP 400 Bad Request error returned for invalid boundary value."
            })

            # 9. Large Payload
            large_body = dict(valid_body)
            large_body[first_key] = "A" * 10000 # 10KB string
            cases.append({
                "title": f"Verify {method} {path} - Large Input Payload",
                "category": "Large payload",
                "priority": "LOW",
                "endpoint": exec_path,
                "method": method,
                "objective": "Verify service handles or limits oversized payload inputs gracefully.",
                "headers": {"Content-Type": "application/json"},
                "params": valid_params,
                "body": large_body,
                "expected_status": 400,
                "expected_result": "HTTP 400 or 413 Payload Too Large error returned."
            })

        return cases

    @staticmethod
    def _build_sample_body(schema: Dict[str, Any]) -> Dict[str, Any]:
        if not schema or not isinstance(schema, dict):
            return {}
        
        properties = schema.get("properties", {})
        if not properties:
            return {"sample_field": "sample_value"}

        sample = {}
        for prop_name, prop_def in properties.items():
            if not isinstance(prop_def, dict):
                sample[prop_name] = "test"
                continue

            p_type = prop_def.get("type", "string")
            if p_type == "string":
                sample[prop_name] = f"sample_{prop_name}"
            elif p_type in ["integer", "number"]:
                sample[prop_name] = 100
            elif p_type == "boolean":
                sample[prop_name] = True
            elif p_type == "array":
                sample[prop_name] = ["item_1", "item_2"]
            elif p_type == "object":
                sample[prop_name] = {"nested_key": "nested_value"}
            else:
                sample[prop_name] = "sample"

        return sample
