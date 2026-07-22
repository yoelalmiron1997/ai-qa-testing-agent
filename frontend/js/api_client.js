const API_BASE = "/api/v1";

const APIClient = {
    // Specs
    async uploadSpec(file) {
        const formData = new FormData();
        formData.append("file", file);
        const res = await fetch(`${API_BASE}/apis/upload`, {
            method: "POST",
            body: formData
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async getSpecs() {
        const res = await fetch(`${API_BASE}/apis`);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async getSpec(specId) {
        const res = await fetch(`${API_BASE}/apis/${specId}`);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    // Risk
    async getRiskAnalysis(specId) {
        const res = await fetch(`${API_BASE}/risk-analysis/${specId}`);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async runRiskAnalysis(specId) {
        const res = await fetch(`${API_BASE}/risk-analysis/${specId}`, { method: "POST" });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    // Test Cases
    async getTestCases(specId, category = "", priority = "") {
        let url = `${API_BASE}/test-cases/${specId}?`;
        if (category) url += `category=${encodeURIComponent(category)}&`;
        if (priority) url += `priority=${encodeURIComponent(priority)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async generateTestCases(specId) {
        const res = await fetch(`${API_BASE}/test-cases/generate/${specId}`, { method: "POST" });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    // Executions
    async runExecution(specId, targetUrl) {
        const res = await fetch(`${API_BASE}/executions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ spec_id: specId, target_url: targetUrl })
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async getExecutionRuns(specId = "") {
        let url = `${API_BASE}/executions`;
        if (specId) url += `?spec_id=${specId}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    async getExecutionResults(runId) {
        const res = await fetch(`${API_BASE}/executions/${runId}/results`);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },

    // Dashboard
    async getDashboardMetrics() {
        const res = await fetch(`${API_BASE}/dashboard`);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    }
};
