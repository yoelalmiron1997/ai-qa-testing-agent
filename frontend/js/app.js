document.addEventListener("DOMContentLoaded", () => {
    // App State
    const state = {
        activeTab: "dashboard",
        activeSpec: null,
        specs: [],
        riskData: null,
        testCases: [],
        executionRuns: [],
        currentRun: null,
        charts: {}
    };

    // Tab Headers Text
    const tabHeaders = {
        dashboard: {
            title: "Quality Assurance Dashboard",
            description: "Overview of loaded API specifications, test scenarios, and execution pass rates."
        },
        import: {
            title: "Import OpenAPI Specification",
            description: "Upload or inspect OpenAPI (JSON/YAML) specs, endpoints, and request schemas."
        },
        risk: {
            title: "Automated Risk Analysis",
            description: "AI evaluation of endpoint security sensitivities, data mutations, and input vectors."
        },
        testcases: {
            title: "AI Test Case Generator",
            description: "Prioritized test scenarios generated across 9 QA testing categories."
        },
        execution: {
            title: "HTTP Execution & AI Diagnosis",
            description: "Real HTTP test runner with live response latency and AI root-cause defect analysis."
        },
        evidence: {
            title: "Evidence Reports & History",
            description: "Standalone HTML evidence reports, Markdown exports, and historical evolution."
        }
    };

    // DOM Elements
    const navItems = document.querySelectorAll(".nav-pill, .nav-item");
    const tabScreens = document.querySelectorAll(".tab-screen");
    const fileInput = document.getElementById("file-input");
    const dropZone = document.getElementById("drop-zone");

    // Init App
    init();

    async function init() {
        bindEvents();
        initCharts();
        await loadSpecs();
        await refreshDashboard();
    }

    function bindEvents() {
        // Tab switching
        navItems.forEach(item => {
            item.addEventListener("click", () => {
                const tab = item.getAttribute("data-tab");
                switchTab(tab);
            });
        });

        // File upload drop zone
        if (dropZone) {
            dropZone.addEventListener("dragover", (e) => {
                e.preventDefault();
                dropZone.style.borderColor = "var(--text-secondary)";
            });

            dropZone.addEventListener("dragleave", () => {
                dropZone.style.borderColor = "var(--border-strong)";
            });

            dropZone.addEventListener("drop", (e) => {
                e.preventDefault();
                dropZone.style.borderColor = "var(--border-strong)";
                if (e.dataTransfer.files.length > 0) {
                    handleFileUpload(e.dataTransfer.files[0]);
                }
            });
        }

        if (fileInput) {
            fileInput.addEventListener("change", (e) => {
                if (e.target.files.length > 0) {
                    handleFileUpload(e.target.files[0]);
                }
            });
        }

        // Quick sample loader button
        document.getElementById("btn-quick-sample")?.addEventListener("click", loadSamplePetstoreSpec);

        // Analyze risk button
        document.getElementById("btn-proceed-risk")?.addEventListener("click", () => switchTab("risk"));
        document.getElementById("btn-reanalyze-risk")?.addEventListener("click", triggerRiskAnalysis);

        // Test generator buttons
        document.getElementById("btn-generate-cases")?.addEventListener("click", generateTestCases);
        document.getElementById("filter-category")?.addEventListener("change", renderTestCases);
        document.getElementById("filter-priority")?.addEventListener("change", renderTestCases);

        // Execution buttons
        document.getElementById("btn-global-run")?.addEventListener("click", () => {
            switchTab("execution");
            runExecution();
        });
        document.getElementById("btn-run-execution")?.addEventListener("click", runExecution);

        // Evidence actions
        document.getElementById("select-history-run")?.addEventListener("change", (e) => loadReportIframe(e.target.value));
        document.getElementById("btn-export-html")?.addEventListener("click", () => {
            const runId = document.getElementById("select-history-run").value;
            if (runId) window.open(`/api/v1/reports/html/${runId}`, "_blank");
        });
        document.getElementById("btn-export-md")?.addEventListener("click", () => {
            const runId = document.getElementById("select-history-run").value;
            if (runId) window.open(`/api/v1/reports/markdown/${runId}`, "_blank");
        });
    }

    function switchTab(tabName) {
        state.activeTab = tabName;

        // Dynamic Header Title Update
        const headerData = tabHeaders[tabName] || tabHeaders.dashboard;
        const pageTitleEl = document.getElementById("page-title");
        const pageDescEl = document.getElementById("page-description");
        if (pageTitleEl) pageTitleEl.innerText = headerData.title;
        if (pageDescEl) pageDescEl.innerText = headerData.description;

        navItems.forEach(btn => {
            if (btn.getAttribute("data-tab") === tabName) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        tabScreens.forEach(screen => {
            if (screen.id === `screen-${tabName}`) {
                screen.classList.add("active");
            } else {
                screen.classList.remove("active");
            }
        });

        // Refresh views based on tab
        if (tabName === "dashboard") refreshDashboard();
        if (tabName === "risk") loadRiskData();
        if (tabName === "testcases") loadTestCases();
        if (tabName === "evidence") loadEvidenceRuns();

        // Refresh icons
        if (window.lucide) lucide.createIcons();
    }

    async function loadSpecs() {
        try {
            state.specs = await APIClient.getSpecs();
            if (state.specs.length > 0) {
                setActiveSpec(state.specs[0]);
            }
        } catch (err) {
            console.error("Error loading specs:", err);
        }
    }

    function setActiveSpec(spec) {
        state.activeSpec = spec;
        document.getElementById("sidebar-spec-title").innerText = spec.title;
        if (document.getElementById("exec-target-url")) {
            document.getElementById("exec-target-url").value = spec.base_url || "http://localhost:8000";
        }
        renderSpecDetails(spec);
    }

    async function handleFileUpload(file) {
        try {
            const spec = await APIClient.uploadSpec(file);
            state.specs.unshift(spec);
            setActiveSpec(spec);
            alert(`API Spec '${spec.title}' imported successfully!`);
        } catch (err) {
            alert(`Error uploading file: ${err.message}`);
        }
    }

    async function loadSamplePetstoreSpec() {
        const sampleYAML = `
openapi: 3.0.0
info:
  title: Petstore & Auth QA Target API
  version: 1.0.0
  description: Sample API for testing Risk Analysis, Scenario Generation, and AI Defect Diagnosis.
servers:
  - url: http://localhost:8000
paths:
  /api/v1/auth/login:
    post:
      summary: User Login Authentication
      description: Authenticates user credentials and returns JWT bearer token.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                username: { type: string }
                password: { type: string }
      responses:
        '200': { description: Login successful }
        '401': { description: Invalid credentials }

  /api/v1/users/profile:
    get:
      summary: Get User Profile
      security: [{ BearerAuth: [] }]
      responses:
        '200': { description: User Profile Object }
        '401': { description: Unauthorized }

  /api/v1/pets:
    get:
      summary: List all pets
      parameters:
        - name: limit
          in: query
          type: integer
      responses:
        '200': { description: List of pets }

  /api/v1/pets/{petId}:
    delete:
      summary: Delete pet record
      parameters:
        - name: petId
          in: path
          required: true
          type: string
      responses:
        '200': { description: Pet deleted }
        '404': { description: Pet not found }
`;
        const blob = new Blob([sampleYAML], { type: "text/yaml" });
        const file = new File([blob], "sample_petstore_openapi.yaml", { type: "text/yaml" });
        await handleFileUpload(file);
    }

    function renderSpecDetails(spec) {
        const viewCard = document.getElementById("spec-parsed-view");
        if (!viewCard) return;

        viewCard.classList.remove("hidden");
        document.getElementById("view-spec-title").innerText = spec.title;
        document.getElementById("view-spec-version").innerText = `v${spec.version}`;
        document.getElementById("view-spec-baseurl").innerText = spec.base_url || "http://localhost:8000";
        document.getElementById("view-endpoint-count").innerText = spec.endpoints_count;

        const container = document.getElementById("endpoints-tree");
        container.innerHTML = "";

        const endpoints = spec.parsed_metadata?.endpoints || [];
        endpoints.forEach(ep => {
            const row = document.createElement("div");
            row.className = "endpoint-row";
            const methodClass = `badge-method-${ep.method.toLowerCase()}`;
            row.innerHTML = `
                <span class="badge ${methodClass}">${ep.method}</span>
                <strong style="font-size:0.9rem;">${ep.path}</strong>
                <span class="text-muted" style="font-size:0.8rem; flex-grow:1;">${ep.summary || ''}</span>
                ${ep.has_auth ? '<span class="badge badge-warning">AUTH REQUIRED</span>' : ''}
            `;
            container.appendChild(row);
        });
    }

    // Risk Analysis
    async function loadRiskData() {
        if (!state.activeSpec) return;
        try {
            state.riskData = await APIClient.getRiskAnalysis(state.activeSpec.id);
            renderRiskData();
        } catch (err) {
            console.error("Risk error:", err);
        }
    }

    async function triggerRiskAnalysis() {
        if (!state.activeSpec) return;
        try {
            state.riskData = await APIClient.runRiskAnalysis(state.activeSpec.id);
            renderRiskData();
        } catch (err) {
            alert(`Risk analysis error: ${err.message}`);
        }
    }

    function renderRiskData() {
        if (!state.riskData) return;
        const badge = document.getElementById("risk-overall-badge");
        badge.innerText = `${state.riskData.overall_risk} RISK (${state.riskData.risk_score}/100)`;
        
        document.getElementById("risk-summary-text").innerText = state.riskData.summary;

        const grid = document.getElementById("risk-cards-grid");
        grid.innerHTML = "";

        (state.riskData.endpoint_risks || []).forEach(ep => {
            const card = document.createElement("div");
            card.className = "risk-card";
            const methodClass = `badge-method-${ep.method.toLowerCase()}`;
            const riskClass = ep.risk_level === "HIGH" ? "badge-fail" : (ep.risk_level === "MEDIUM" ? "badge-warning" : "badge-pass");

            const reasonsHtml = ep.reasons.map(r => `<li style="font-size:0.82rem; color:var(--text-secondary); margin-top:0.25rem;">${r}</li>`).join("");

            card.innerHTML = `
                <div class="risk-card-header">
                    <div>
                        <span class="badge ${methodClass}">${ep.method}</span>
                        <strong style="margin-left:0.5rem; font-size:0.95rem;">${ep.endpoint}</strong>
                    </div>
                    <span class="badge ${riskClass}">${ep.risk_level} (${ep.risk_score})</span>
                </div>
                <ul style="padding-left:1.2rem; margin-top:0.5rem;">
                    ${reasonsHtml}
                </ul>
            `;
            grid.appendChild(card);
        });
    }

    // Test Cases
    async function loadTestCases() {
        if (!state.activeSpec) return;
        try {
            const category = document.getElementById("filter-category").value;
            const priority = document.getElementById("filter-priority").value;
            state.testCases = await APIClient.getTestCases(state.activeSpec.id, category, priority);
            renderTestCases();
        } catch (err) {
            console.error("Test cases error:", err);
        }
    }

    async function generateTestCases() {
        if (!state.activeSpec) return;
        try {
            state.testCases = await APIClient.generateTestCases(state.activeSpec.id);
            renderTestCases();
        } catch (err) {
            alert(`Error generating cases: ${err.message}`);
        }
    }

    function renderTestCases() {
        const grid = document.getElementById("testcases-list");
        if (!grid) return;
        grid.innerHTML = "";

        const categoryFilter = document.getElementById("filter-category").value.toLowerCase();
        const priorityFilter = document.getElementById("filter-priority").value.toLowerCase();

        const filtered = state.testCases.filter(tc => {
            const matchCat = !categoryFilter || tc.category.toLowerCase() === categoryFilter;
            const matchPrio = !priorityFilter || tc.priority.toLowerCase() === priorityFilter;
            return matchCat && matchPrio;
        });

        if (filtered.length === 0) {
            grid.innerHTML = `<div class="card center text-muted" style="grid-column:1/-1; padding:2.5rem; background: var(--bg-panel); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);">No test cases match the active filter criteria. Click 'Generate AI Test Suite' to create scenarios.</div>`;
            return;
        }

        filtered.forEach(tc => {
            const card = document.createElement("div");
            card.className = "tc-card";
            const methodClass = `badge-method-${tc.method.toLowerCase()}`;
            
            card.innerHTML = `
                <div class="tc-header">
                    <div>
                        <span class="badge ${methodClass}">${tc.method}</span>
                        <strong style="font-size:0.95rem; margin-left:0.4rem;">${tc.title}</strong>
                    </div>
                    <span class="badge badge-warning">${tc.priority}</span>
                </div>
                <div style="font-size:0.83rem; color:var(--text-secondary); margin-bottom:0.75rem;">
                    <strong>Category:</strong> ${tc.category}<br>
                    <strong>Endpoint:</strong> <code>${tc.endpoint}</code><br>
                    <strong>Objective:</strong> ${tc.objective}
                </div>
                <div style="background:#09090b; border:1px solid var(--border-subtle); border-radius:6px; padding:0.5rem; font-size:0.78rem;">
                    <strong>Expected Status:</strong> HTTP ${tc.expected_status}
                </div>
            `;
            grid.appendChild(card);
        });
    }

    // Execution
    async function runExecution() {
        if (!state.activeSpec) {
            alert("Please import an API specification first!");
            return;
        }

        const targetUrl = document.getElementById("exec-target-url").value || "http://localhost:8000";
        const progressWrap = document.getElementById("exec-progress-wrap");
        const progressFill = document.getElementById("exec-progress-fill");
        const resultsList = document.getElementById("exec-results-list");

        progressWrap.classList.remove("hidden");
        progressFill.style.width = "40%";
        resultsList.innerHTML = `<div class="card center" style="padding:2.5rem; background: var(--bg-panel); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);"><i data-lucide="loader" class="spin"></i> Executing real HTTP scenarios against ${targetUrl}...</div>`;
        if (window.lucide) lucide.createIcons();

        try {
            const run = await APIClient.runExecution(state.activeSpec.id, targetUrl);
            progressFill.style.width = "100%";
            state.currentRun = run;

            const results = await APIClient.getExecutionResults(run.id);
            renderExecutionResults(run, results);
            refreshDashboard();
        } catch (err) {
            resultsList.innerHTML = `<div class="card center badge-fail" style="padding:2.5rem;">Execution Error: ${err.message}</div>`;
        }
    }

    async function renderExecutionResults(run, results) {
        const resultsList = document.getElementById("exec-results-list");
        resultsList.innerHTML = "";

        results.forEach(res => {
            const card = document.createElement("div");
            card.className = "result-item-card";
            const isPass = res.status === "PASS";
            const badgeClass = isPass ? "badge-pass" : "badge-fail";

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                    <div>
                        <span class="badge ${badgeClass}">${res.status} (${res.status_code || 'ERR'})</span>
                        <strong style="margin-left:0.5rem; font-size:1rem;">${res.expected_summary || 'Scenario'}</strong>
                    </div>
                    <span class="text-muted" style="font-size:0.83rem;">${res.latency_ms} ms</span>
                </div>
                <div style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:0.5rem;">
                    URL: <code>${res.request_url}</code>
                </div>
                ${res.error_details ? `<div style="font-size:0.85rem; color:var(--accent-rose); margin-top:0.3rem;">Error: ${res.error_details}</div>` : ''}
            `;
            resultsList.appendChild(card);
        });
    }

    // Evidence
    async function loadEvidenceRuns() {
        if (!state.activeSpec) return;
        try {
            const runs = await APIClient.getExecutionRuns(state.activeSpec.id);
            const select = document.getElementById("select-history-run");
            select.innerHTML = `<option value="">Select Execution Run</option>`;

            runs.forEach(r => {
                const opt = document.createElement("option");
                opt.value = r.id;
                opt.innerText = `Run ${r.id.substring(0,8)} - ${r.pass_rate}% Pass (${new Date(r.created_at).toLocaleTimeString()})`;
                select.appendChild(opt);
            });

            if (runs.length > 0) {
                select.value = runs[0].id;
                loadReportIframe(runs[0].id);
            }
        } catch (err) {
            console.error("Evidence error:", err);
        }
    }

    function loadReportIframe(runId) {
        const iframe = document.getElementById("report-iframe");
        if (runId) {
            iframe.src = `/api/v1/reports/html/${runId}`;
        }
    }

    // Dashboard & Charts
    async function refreshDashboard() {
        try {
            const data = await APIClient.getDashboardMetrics();
            document.getElementById("dash-total-apis").innerText = data.total_apis;
            document.getElementById("dash-total-endpoints").innerText = data.total_endpoints;
            document.getElementById("dash-total-tests").innerText = data.total_test_cases;
            document.getElementById("dash-pass-rate").innerText = `${data.overall_pass_rate}%`;

            updateCharts(data);
        } catch (err) {
            console.error("Dashboard metrics error:", err);
        }
    }

    function initCharts() {
        const ctx1 = document.getElementById("chart-pass-fail")?.getContext("2d");
        const ctx2 = document.getElementById("chart-evolution")?.getContext("2d");

        if (ctx1) {
            state.charts.passFail = new Chart(ctx1, {
                type: "doughnut",
                data: {
                    labels: ["Passed", "Failed"],
                    datasets: [{
                        data: [0, 0],
                        backgroundColor: ["#10b981", "#f43f5e"],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: "#a1a1aa" } } }
                }
            });
        }

        if (ctx2) {
            state.charts.evolution = new Chart(ctx2, {
                type: "line",
                data: {
                    labels: [],
                    datasets: [{
                        label: "Pass Rate (%)",
                        data: [],
                        borderColor: "#f4f4f5",
                        tension: 0.3,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { ticks: { color: "#71717a" }, grid: { color: "#27272a" } },
                        y: { min: 0, max: 100, ticks: { color: "#71717a" }, grid: { color: "#27272a" } }
                    },
                    plugins: { legend: { labels: { color: "#a1a1aa" } } }
                }
            });
        }
    }

    function updateCharts(data) {
        if (state.charts.passFail) {
            state.charts.passFail.data.datasets[0].data = [data.total_passed, data.total_failed];
            state.charts.passFail.update();
        }

        if (state.charts.evolution && data.evolution) {
            state.charts.evolution.data.labels = data.evolution.map(e => e.created_at);
            state.charts.evolution.data.datasets[0].data = data.evolution.map(e => e.pass_rate);
            state.charts.evolution.update();
        }
    }
});
