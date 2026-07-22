import pytest
from app.services.openapi_parser import OpenAPIParser

SAMPLE_YAML_SPEC = """
openapi: 3.0.0
info:
  title: Test Auth API
  version: 2.1.0
  description: Authentication Service API
servers:
  - url: https://api.testservice.com
paths:
  /auth/login:
    post:
      summary: Login user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username: { type: string }
                password: { type: string }
      responses:
        '200':
          description: Login successful
"""

def test_parse_yaml_spec():
    parsed = OpenAPIParser.parse_spec_content(SAMPLE_YAML_SPEC, "auth_spec.yaml")
    assert parsed["title"] == "Test Auth API"
    assert parsed["version"] == "2.1.0"
    assert parsed["base_url"] == "https://api.testservice.com"
    assert parsed["endpoints_count"] == 1
    assert parsed["endpoints"][0]["path"] == "/auth/login"
    assert parsed["endpoints"][0]["method"] == "POST"

def test_parse_invalid_format():
    with pytest.raises(ValueError):
        OpenAPIParser.parse_spec_content("INVALID_CONTENT: [[[", "bad.json")
