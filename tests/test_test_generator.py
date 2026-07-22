from app.services.test_generator import TestGenerator

def test_test_generator_scenario_categories():
    spec_meta = {
        "endpoints": [
            {
                "path": "/users/profile",
                "method": "POST",
                "has_auth": True,
                "parameters": [],
                "request_body_schema": {
                    "properties": {
                        "email": {"type": "string"},
                        "age": {"type": "integer"}
                    }
                }
            }
        ]
    }

    scenarios = TestGenerator.generate_test_cases_for_spec(spec_meta)
    assert len(scenarios) >= 5

    categories = [s["category"] for s in scenarios]
    assert "Functional" in categories
    assert "Security" in categories
    assert "Authorization" in categories
    assert "Missing fields" in categories
    assert "Unexpected types" in categories
