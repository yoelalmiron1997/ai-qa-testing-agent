# 🤖 AI QA Testing Agent Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade autonomous AI QA platform designed for QA Engineers to analyze REST APIs documented with OpenAPI/Swagger specifications, perform automated endpoint risk assessment, generate multi-dimensional test scenarios, execute real HTTP assertions, diagnose root-cause defects, and generate evidence-backed quality reports.

---

## 🚀 Key Features

* **📄 OpenAPI/Swagger Parsing**: Ingests `openapi.json`, `swagger.json`, or `.yaml` files (OpenAPI 2.0 / 3.0 / 3.1). Automatically extracts endpoints, parameters, request body schemas, response codes, and security requirements.
* **🛡️ Endpoint Risk Analysis**: Automatically evaluates endpoints based on security sensitivity, authentication requirements, state mutation methods (`POST`, `PUT`, `DELETE`), user input vectors, and dynamic path parameters. Assigns `HIGH`, `MEDIUM`, or `LOW` risk ratings with bulleted rationale explanations.
* **⚡ 9-Dimension Test Scenario Generator**: Generates prioritized test cases covering:
  1. **Functional** (Happy Path)
  2. **Boundary** (Edge values, empty strings)
  3. **Negative** (404 non-existent resource IDs)
  4. **Security** (Missing authentication tokens)
  5. **Authorization** (Invalid or expired bearer tokens)
  6. **Invalid Payload** (Malformed JSON/empty body)
  7. **Missing Fields** (Omitting required properties)
  8. **Large Payload** (Oversized input strings)
  9. **Unexpected Types** (Passing boolean/string instead of integer)
* **🌐 Real HTTP Execution Engine**: Executes real HTTP requests against designated base target URLs. Measures response latency in milliseconds (`ms`), captures status codes, request/response headers, and validates JSON schemas.
* **🧠 AI Defect Diagnostic Engine**: Performs automated root cause analysis whenever a test fails or returns unexpected HTTP status codes (e.g., HTTP 500 returned instead of 404/400). Provides confidence scores (`HIGH`, `MEDIUM`, `LOW`), explains the failure mechanism, and delivers developer fix recommendations.
* **📄 Evidence & Professional Reports**: Generates standalone **Jinja2 HTML Reports** and **Markdown Summaries** with metric badges, payload code blocks, and inline AI defect diagnostics.
* **📊 Quality Dashboard & Evolution**: SQLite database tracking specifications, risk analyses, test cases, execution runs, test results, and historical pass rate trends over time.

---

## 🏗️ Architecture & Project Structure

The project follows **Clean Architecture** principles to separate domain logic, agent reasoning, executable tools, storage, and API controllers.

```
ai-qa-testing-agent/
├── app/
│   ├── main.py                  # FastAPI application entry point & static UI mount
│   ├── core/                    # Settings, Database engine, LLM client factory
│   │   ├── config.py
│   │   ├── database.py
│   │   └── llm.py
│   ├── storage/                 # SQLAlchemy Entities & Repository Layer
│   │   ├── models.py
│   │   └── repository.py
│   ├── services/                # Domain & Business logic engines
│   │   ├── openapi_parser.py
│   │   ├── risk_analyzer.py
│   │   ├── test_generator.py
│   │   ├── test_runner.py
│   │   ├── defect_analyzer.py
│   │   ├── report_service.py
│   │   └── analytics_service.py
│   ├── agent/                   # Autonomous AI QA Agent Orchestration
│   │   ├── qa_agent.py
│   │   └── prompts.py
│   ├── tools/                   # Decoupled Executable Agent Tools
│   │   ├── base.py
│   │   ├── openapi_tool.py
│   │   ├── http_tool.py
│   │   ├── schema_tool.py
│   │   └── report_tool.py
│   ├── reports/                 # Jinja2 Evidence Report Templates
│   │   └── templates/
│   │       └── report.html.j2
│   └── api/
│       └── v1/                  # REST API Endpoints
│           ├── apis.py
│           ├── risk.py
│           ├── testcases.py
│           ├── executions.py
│           ├── ai_analysis.py
│           ├── reports.py
│           └── dashboard.py
├── frontend/                    # Modern Dark SPA (Linear / Vercel style)
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api_client.js
│       └── app.js
├── tests/                       # Pytest Automated Test Suite
│   ├── test_openapi_parser.py
│   ├── test_risk_analyzer.py
│   ├── test_test_generator.py
│   └── test_defect_analyzer.py
├── Dockerfile                   # Production Docker Container Definition
├── docker-compose.yml           # Container Orchestration
└── requirements.txt             # Project Dependencies
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.10+ (or Docker)
- Git

### Option 1: Running with Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yoelalmiron1997/ai-qa-testing-agent.git
   cd ai-qa-testing-agent
   ```
2. Launch with Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Open your browser at `http://localhost:8000`.

### Option 2: Running Locally with Virtual Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yoelalmiron1997/ai-qa-testing-agent.git
   cd ai-qa-testing-agent
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Uvicorn dev server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Open your browser at `http://localhost:8000`.

---

## 🧪 Running Automated Tests

Run the `pytest` test suite:

```bash
pytest tests/ -v
```

---

## 🔮 Platform Extensibility Roadmap

Designed as a foundation for a complete **AI QA Platform**:
- 🎭 **Playwright / Cypress Integration**: E2E web flow validation extension.
- 🤖 **Robot Framework Exporter**: Export test suites to `.robot` format.
- 🔌 **MCP Server Support**: Expose QA tools via Model Context Protocol.
- 🎫 **Jira & GitHub Issues Connector**: Automatically publish high-confidence defects as tickets.
- 📈 **Prometheus & Grafana Exporter**: Metrics monitoring via `/metrics`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
