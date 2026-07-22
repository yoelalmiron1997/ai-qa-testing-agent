# 🤖 AI QA Testing Agent Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Plataforma empresarial de Agente de IA autónomo diseñada para ingenieros de QA. Analiza especificaciones REST API documentadas con OpenAPI/Swagger, realiza evaluación automática de riesgos en endpoints, genera escenarios de prueba multidimensionales, ejecuta aserciones HTTP reales, diagnostica defectos con razonamiento de causa raíz y produce reportes profesionales respaldados con evidencia.

---

## 🚀 Funcionalidades Principales

* **📄 Lectura e Inspección OpenAPI/Swagger**: Procesa archivos `openapi.json`, `swagger.json` o `.yaml` (OpenAPI 2.0 / 3.0 / 3.1). Extrae automáticamente endpoints, parámetros, esquemas de entrada, códigos de respuesta y requisitos de seguridad.
* **🛡️ Análisis de Riesgo por Endpoint**: Evalúa automáticamente el riesgo de cada endpoint basándose en sensibilidad de seguridad, autenticación requerida, métodos de mutación de datos (`POST`, `PUT`, `DELETE`), vectores de entrada de usuario y parámetros de ruta. Asigna clasificaciones `HIGH`, `MEDIUM` o `LOW` acompañadas de la justificación técnica.
* **⚡ Generador de Pruebas en 9 Dimensiones**: Genera casos de prueba priorizados cubriendo:
  1. **Functional** (Camino feliz)
  2. **Boundary** (Valores límite y cadenas vacías)
  3. **Negative** (Recursos no existentes / HTTP 404)
  4. **Security** (Acceso sin token de autenticación)
  5. **Authorization** (Tokens inválidos o expirados)
  6. **Invalid Payload** (Cuerpos JSON malformados o vacíos)
  7. **Missing Fields** (Omisión de campos requeridos)
  8. **Large Payload** (Entradas con cargas masivas)
  9. **Unexpected Types** (Tipos de datos incorrectos, ej: booleano por entero)
* **🌐 Motor de Ejecución HTTP Real**: Realiza solicitudes HTTP reales contra el API objetivo. Mide el tiempo de respuesta exacto en milisegundos (`ms`), captura códigos de estado, cabeceras y valida esquemas de respuesta JSON.
* **🧠 Diagnóstico de Defectos por IA**: Realiza un análisis automatizado de causa raíz cada vez que una prueba falla o devuelve un código inesperado (ej: HTTP 500 en lugar de 404/400). Emite un nivel de confianza (`HIGH`, `MEDIUM`, `LOW`), explica el mecanismo de falla y ofrece recomendaciones concretas para los desarrolladores.
* **📄 Reportes Profesionales con Evidencia**: Produce reportes **HTML independientes (Jinja2)** e informes en **Markdown** con insignias métricas, fragmentos de código payload/respuesta y tarjetas de diagnóstico de IA.
* **📊 Panel de Control y Evolución de Calidad**: Base de datos SQLite que registra especificaciones, análisis de riesgo, casos de prueba, corridas de ejecución, resultados detallados y gráficos de evolución de pass rate a lo largo del tiempo.

---

## 🏗️ Arquitectura y Estructura del Proyecto

El proyecto sigue los principios de **Clean Architecture** (Arquitectura Limpia) para separar el dominio de negocio, el razonamiento del agente, las herramientas ejecutables, el almacenamiento y los controladores REST.

```
ai-qa-testing-agent/
├── app/
│   ├── main.py                  # Punto de entrada FastAPI y servidor de UI estática
│   ├── core/                    # Configuración, motor de Base de Datos y cliente LLM
│   │   ├── config.py
│   │   ├── database.py
│   │   └── llm.py
│   ├── storage/                 # Entidades SQLAlchemy y Repositorio de Datos
│   │   ├── models.py
│   │   └── repository.py
│   ├── services/                # Motores de Lógica de Negocio
│   │   ├── openapi_parser.py
│   │   ├── risk_analyzer.py
│   │   ├── test_generator.py
│   │   ├── test_runner.py
│   │   ├── defect_analyzer.py
│   │   ├── report_service.py
│   │   └── analytics_service.py
│   ├── agent/                   # Orquestador del Agente de IA de QA
│   │   ├── qa_agent.py
│   │   └── prompts.py
│   ├── tools/                   # Herramientas Ejecutables Desacopladas
│   │   ├── base.py
│   │   ├── openapi_tool.py
│   │   ├── http_tool.py
│   │   ├── schema_tool.py
│   │   └── report_tool.py
│   ├── reports/                 # Plantillas Jinja2 para Reportes
│   │   └── templates/
│   │       └── report.html.j2
│   └── api/
│       └── v1/                  # Rutas y Controladores REST API
│           ├── apis.py
│           ├── risk.py
│           ├── testcases.py
│           ├── executions.py
│           ├── ai_analysis.py
│           ├── reports.py
│           └── dashboard.py
├── frontend/                    # SPA Tema Oscuro Moderno (Estilo Linear / Vercel)
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api_client.js
│       └── app.js
├── tests/                       # Batería de Pruebas Automatizadas (Pytest)
│   ├── test_openapi_parser.py
│   ├── test_risk_analyzer.py
│   ├── test_test_generator.py
│   └── test_defect_analyzer.py
├── Dockerfile                   # Definición de Contenedor Docker de Producción
├── docker-compose.yml           # Orquestación de Contenedor
└── requirements.txt             # Dependencias del Proyecto
```

---

## ⚙️ Guía de Inicio Rápido

### Requisitos Previos
- Python 3.10+ (o Docker)
- Git

### Opción 1: Ejecución con Docker Compose (Recomendado)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/yoelalmiron1997/ai-qa-testing-agent.git
   cd ai-qa-testing-agent
   ```
2. Inicia la aplicación con Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Abre tu navegador en `http://localhost:8000`.

### Opción 2: Ejecución Local con Entorno Virtual (Python)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/yoelalmiron1997/ai-qa-testing-agent.git
   cd ai-qa-testing-agent
   ```
2. Crea y activa el entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/macOS:
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Inicia el servidor Uvicorn:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Abre tu navegador en `http://localhost:8000`.

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite de pruebas unitarias e integración con `pytest`:

```bash
pytest tests/ -v
```

---

## 🔮 Roadmap de Extensibilidad

Diseñado como la base de una plataforma integral de **AI QA Platform**:
- 🎭 **Integración con Playwright / Cypress**: Validación de flujos web E2E.
- 🤖 **Exportador Robot Framework**: Generación directa de archivos `.robot`.
- 🔌 **Servidores MCP**: Exposición de capacidades vía Model Context Protocol.
- 🎫 **Conector con Jira y GitHub Issues**: Publicación automática de defectos diagnosticados como tickets.
- 📈 **Exportador Prometheus y Grafana**: Monitoreo de métricas vía `/metrics`.

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.
