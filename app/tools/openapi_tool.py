from typing import Dict, Any
from app.tools.base import BaseTool
from app.services.openapi_parser import OpenAPIParser

class ReadOpenAPITool(BaseTool):
    name = "read_openapi"
    description = "Parses raw OpenAPI/Swagger JSON or YAML content into structured endpoint metadata."

    def execute(self, content: str, filename: str = "") -> Dict[str, Any]:
        return OpenAPIParser.parse_spec_content(content, filename)
