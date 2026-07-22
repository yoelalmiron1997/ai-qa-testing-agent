from typing import Dict, Any, List
from app.core.llm import llm_client

class RiskAnalyzer:
    """
    Automated Endpoint & API Risk Analysis Service.
    Evaluates HTTP endpoints based on security sensitivity, authentication requirements,
    data mutations, user inputs, complex schemas, and potential impact.
    """

    @staticmethod
    def analyze_api_risk(spec_metadata: Dict[str, Any]) -> Dict[str, Any]:
        endpoints = spec_metadata.get("endpoints", [])
        endpoint_risks: List[Dict[str, Any]] = []

        total_score = 0.0

        for ep in endpoints:
            ep_risk = RiskAnalyzer._evaluate_endpoint(ep)
            endpoint_risks.append(ep_risk)
            total_score += ep_risk["risk_score"]

        avg_score = round(total_score / max(len(endpoints), 1), 1)
        overall_level = "HIGH" if avg_score >= 65 else ("MEDIUM" if avg_score >= 35 else "LOW")

        summary = f"API risk evaluated across {len(endpoints)} endpoints. Overall risk level: {overall_level} (Score: {avg_score}/100)."

        fallback_result = {
            "overall_risk": overall_level,
            "risk_score": avg_score,
            "summary": summary,
            "endpoint_risks": endpoint_risks
        }

        # Optional LLM refinement if key is available
        system_prompt = """You are an Expert AI Security & QA Engineer. Review the API risk assessment and return a structured JSON summary."""
        user_prompt = f"API Title: {spec_metadata.get('title')}\nEndpoints Risk Summary:\n{endpoint_risks[:10]}"
        
        return llm_client.generate_json(system_prompt, user_prompt, fallback_result)

    @staticmethod
    def _evaluate_endpoint(endpoint: Dict[str, Any]) -> Dict[str, Any]:
        path = endpoint.get("path", "")
        method = endpoint.get("method", "GET").upper()
        has_auth = endpoint.get("has_auth", False)
        parameters = endpoint.get("parameters", [])
        has_body = endpoint.get("request_body_schema") is not None

        reasons = []
        score = 20.0 # Base score

        # Auth & Security Sensitivity
        auth_keywords = ["login", "auth", "token", "password", "signup", "user", "admin", "secret", "payment", "card"]
        if any(k in path.lower() for k in auth_keywords):
            score += 35.0
            reasons.append("Security Sensitive Path (Auth/User/Payment handling)")

        if not has_auth and method in ["POST", "PUT", "DELETE", "PATCH"]:
            score += 25.0
            reasons.append("Unauthenticated Data Mutation Method")

        if has_auth:
            score += 15.0
            reasons.append("Authentication & Authorization Enforcement")

        # HTTP Method Impact
        if method in ["DELETE"]:
            score += 25.0
            reasons.append("Destructive Operation (DELETE)")
        elif method in ["POST", "PUT", "PATCH"]:
            score += 20.0
            reasons.append("State Changing Operation (POST/PUT/PATCH)")

        # User Input Complexity
        if len(parameters) > 3 or has_body:
            score += 15.0
            reasons.append("User Input Payload Processing")

        # Sensitive parameter checks
        param_names = [p.get("name", "").lower() for p in parameters]
        if any(k in param_names for k in ["id", "uuid", "file", "upload", "query", "sql"]):
            score += 10.0
            reasons.append("Dynamic Parameter Injection Vector")

        score = min(round(score, 1), 100.0)
        risk_level = "HIGH" if score >= 65 else ("MEDIUM" if score >= 35 else "LOW")

        return {
            "endpoint": path,
            "method": method,
            "risk_level": risk_level,
            "risk_score": score,
            "reasons": reasons if reasons else ["Standard read-only endpoint"]
        }
