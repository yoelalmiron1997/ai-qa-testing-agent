import json
import jsonschema
from typing import Dict, Any
from app.tools.base import BaseTool

class CompareSchemaTool(BaseTool):
    name = "compare_schema"
    description = "Validates an HTTP JSON response body against expected JSON schema definition."

    def execute(self, response_body: str, expected_schema: Dict[str, Any]) -> Dict[str, Any]:
        if not response_body or not expected_schema:
            return {"is_valid": True, "error": None}
        
        try:
            instance = json.loads(response_body)
            jsonschema.validate(instance=instance, schema=expected_schema)
            return {"is_valid": True, "error": None}
        except json.JSONDecodeError as e:
            return {"is_valid": False, "error": f"Invalid JSON response body: {str(e)}"}
        except jsonschema.ValidationError as e:
            return {"is_valid": False, "error": f"Schema Mismatch: {e.message} at path {list(e.path)}"}
        except Exception as e:
            return {"is_valid": False, "error": f"Validation Exception: {str(e)}"}
