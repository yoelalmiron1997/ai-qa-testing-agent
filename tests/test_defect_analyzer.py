from app.services.defect_analyzer import DefectAnalyzer

def test_defect_analyzer_detects_500_error():
    tc = {
        "title": "Verify User Profile",
        "category": "Functional",
        "endpoint": "/users/profile",
        "method": "GET",
        "expected_status": 200
    }

    result = {
        "status": "FAIL",
        "status_code": 500,
        "response_body": "Internal Server Error: NullPointerException",
        "error_details": "Expected HTTP status 200, but received HTTP status 500."
    }

    diagnosis = DefectAnalyzer.analyze_result(tc, result)
    assert diagnosis["is_defect"] is True
    assert diagnosis["confidence"] == "HIGH"
    assert "500" in diagnosis["possible_defect"] or "Internal Server Error" in diagnosis["possible_defect"]
    assert diagnosis["recommendation"] is not None
