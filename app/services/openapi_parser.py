import json
import yaml
from typing import Dict, Any, List, Optional

class OpenAPIParser:
    """
    Parser for OpenAPI 2.0 / 3.0 / 3.1 specifications (JSON and YAML).
    Extracts structured endpoint metadata, request/response schemas, security, and base server URLs.
    """

    @staticmethod
    def parse_spec_content(content: str, filename_hint: str = "") -> Dict[str, Any]:
        """
        Parses raw text content as JSON or YAML.
        """
        content_stripped = content.strip()
        is_yaml = filename_hint.endswith((".yaml", ".yml")) or not (content_stripped.startswith("{") or content_stripped.startswith("["))
        
        try:
            if is_yaml:
                raw_dict = yaml.safe_load(content)
                spec_format = "yaml"
            else:
                raw_dict = json.loads(content)
                spec_format = "json"
        except Exception as e:
            raise ValueError(f"Invalid OpenAPI format ({'YAML' if is_yaml else 'JSON'}): {str(e)}")

        if not isinstance(raw_dict, dict):
            raise ValueError("Parsed OpenAPI spec must be a dictionary object.")

        return OpenAPIParser.extract_metadata(raw_dict, spec_format, content)

    @staticmethod
    def extract_metadata(raw_dict: Dict[str, Any], spec_format: str, raw_content: str) -> Dict[str, Any]:
        info = raw_dict.get("info", {})
        title = info.get("title", "Untitled API")
        version = info.get("version", "1.0.0")
        description = info.get("description", "")

        # Extract base server URL
        base_url = "http://localhost:8000"
        if "servers" in raw_dict and isinstance(raw_dict["servers"], list) and len(raw_dict["servers"]) > 0:
            base_url = raw_dict["servers"][0].get("url", base_url)
        elif "host" in raw_dict:
            schemes = raw_dict.get("schemes", ["http"])
            base_path = raw_dict.get("basePath", "")
            base_url = f"{schemes[0]}://{raw_dict['host']}{base_path}"

        # Normalize trailing slash
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        # Security definitions / requirements
        security_schemes = raw_dict.get("components", {}).get("securitySchemes", {}) or raw_dict.get("securityDefinitions", {})
        global_security = raw_dict.get("security", [])

        endpoints: List[Dict[str, Any]] = []
        paths = raw_dict.get("paths", {})

        http_methods = ["get", "post", "put", "delete", "patch", "options", "head"]

        for path_str, path_obj in paths.items():
            if not isinstance(path_obj, dict):
                continue
            
            # Common path parameters
            common_params = path_obj.get("parameters", [])

            for method_str, op_obj in path_obj.items():
                if method_str.lower() not in http_methods or not isinstance(op_obj, dict):
                    continue

                method = method_str.upper()
                summary = op_obj.get("summary", "")
                op_description = op_obj.get("description", "")
                operation_id = op_obj.get("operationId", f"{method.lower()}_{path_str.replace('/', '_')}")
                tags = op_obj.get("tags", [])

                # Consolidate parameters
                op_params = op_obj.get("parameters", [])
                all_params = list(common_params) + list(op_params)
                
                parsed_params: List[Dict[str, Any]] = []
                for p in all_params:
                    if isinstance(p, dict):
                        parsed_params.append({
                            "name": p.get("name"),
                            "in": p.get("in"), # path, query, header, cookie, body
                            "required": p.get("required", False),
                            "type": p.get("type") or p.get("schema", {}).get("type", "string"),
                            "description": p.get("description", ""),
                            "schema": p.get("schema", {})
                        })

                # Request body (OpenAPI 3.x vs Swagger 2.0)
                request_body_schema = None
                if "requestBody" in op_obj:
                    content_obj = op_obj["requestBody"].get("content", {})
                    for content_type, media_type in content_obj.items():
                        request_body_schema = media_type.get("schema", {})
                        break
                else:
                    # Swagger 2.0 body parameter check
                    for p in parsed_params:
                        if p.get("in") == "body":
                            request_body_schema = p.get("schema", {})
                            break

                # Response status codes & schemas
                responses = op_obj.get("responses", {})
                parsed_responses = {}
                for code, resp_obj in responses.items():
                    if isinstance(resp_obj, dict):
                        parsed_responses[str(code)] = {
                            "description": resp_obj.get("description", ""),
                            "schema": resp_obj.get("schema") or resp_obj.get("content", {}).get("application/json", {}).get("schema", {})
                        }

                # Endpoint security requirement
                endpoint_security = op_obj.get("security", global_security)
                has_auth = len(endpoint_security) > 0 or bool(security_schemes)

                endpoints.append({
                    "path": path_str,
                    "method": method,
                    "summary": summary,
                    "description": op_description,
                    "operation_id": operation_id,
                    "tags": tags,
                    "parameters": parsed_params,
                    "request_body_schema": request_body_schema,
                    "responses": parsed_responses,
                    "has_auth": has_auth,
                    "security_requirements": endpoint_security
                })

        return {
            "title": title,
            "version": version,
            "description": description,
            "base_url": base_url,
            "format": spec_format,
            "raw_content": raw_content,
            "endpoints_count": len(endpoints),
            "endpoints": endpoints,
            "security_schemes": security_schemes
        }
