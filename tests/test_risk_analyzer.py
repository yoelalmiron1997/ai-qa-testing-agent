from app.services.risk_analyzer import RiskAnalyzer

def test_risk_analysis_security_sensitive_endpoint():
    spec_meta = {
        "title": "Auth API",
        "endpoints": [
            {
                "path": "/auth/login",
                "method": "POST",
                "has_auth": False,
                "parameters": [{"name": "username"}, {"name": "password"}],
                "request_body_schema": {"properties": {"username": {}, "password": {}}}
            }
        ]
    }

    analysis = RiskAnalyzer.analyze_api_risk(spec_meta)
    assert "overall_risk" in analysis
    assert analysis["overall_risk"] in ["HIGH", "MEDIUM", "LOW"]
    assert len(analysis["endpoint_risks"]) == 1
    assert analysis["endpoint_risks"][0]["risk_level"] == "HIGH"
