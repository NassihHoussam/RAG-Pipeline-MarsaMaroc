const API_BASE = "";

let chunkingCoherenceChartInstance = null;
let chunkingSizeChartInstance = null;
let embeddingChartInstance = null;
let retrievalChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    initTabNavigation();
    fetchDatasetInfo();
    fetchVectorialStatus();
    loadChunkingMetrics();
    loadEmbeddingMetrics();
    
    document.getElementById("btn-run-query").addEventListener("click", runQuery);
    document.getElementById("btn-run-retrieval-eval").addEventListener("click", runRetrievalBenchmark);
    document.getElementById("btn-refresh-chunk-metrics").addEventListener("click", loadChunkingMetrics);
    document.getElementById("btn-refresh-emb-metrics").addEventListener("click", loadEmbeddingMetrics);

    document.querySelectorAll(".btn-chunk").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".btn-chunk").forEach(b => b.classList.remove("active"));
            e.currentTarget.classList.add("active");
            const method = e.currentTarget.getAttribute("data-method");
            runChunkingMethod(method);
        });
    });
});

function initTabNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const tabId = item.getAttribute("data-tab");
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

    const selectedNav = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
    const selectedTab = document.getElementById(tabId);

    if (selectedNav) selectedNav.classList.add("active");
    if (selectedTab) selectedTab.classList.add("active");

    if (tabId === 'retrieval-tab' && !retrievalChartInstance) {
        runRetrievalBenchmark();
    }
}

async function fetchDatasetInfo() {
    try {
        const res = await fetch(`${API_BASE}/dataset/info`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById("pdf-title").innerText = data.filename || "Document_Data_Reduit.pdf";
            document.getElementById("pdf-pages").innerText = `${data.valid_pages || 100} pages • ${data.total_words || 0} mots`;
        }
    } catch (err) {
        console.warn("API Connection error:", err);
    }
}

async function fetchVectorialStatus() {
    try {
        const res = await fetch(`${API_BASE}/vectorial`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById("stat-chunks").innerText = data.total_chunks || "--";
            document.getElementById("stat-dim").innerText = data.vector_dimension || "300";
        }
    } catch (err) {
        console.warn("Vectorial status error:", err);
    }
}

async function runQuery() {
    const queryInput = document.getElementById("user-query").value.trim();
    const retrievalMethod = document.getElementById("retrieval-method-select").value;
    const topKSelect = document.getElementById("top-k-select");
    const topK = topKSelect ? parseInt(topKSelect.value) : 5;

    if (!queryInput) return;

    const responseBox = document.getElementById("response-output");
    const confidenceBadge = document.getElementById("confidence-badge");

    responseBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Recherche vectorielle et génération de la réponse en cours...';

    try {
        const res = await fetch(`${API_BASE}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: queryInput,
                retrieval_method: retrievalMethod,
                top_k: topK
            })
        });

        if (res.ok) {
            const data = await res.json();
            let formattedAnswer = data.response
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');

            responseBox.innerHTML = formattedAnswer;
            confidenceBadge.innerText = `Confiance: ${(data.confidence_score * 100).toFixed(0)}%`;
        } else {
            responseBox.innerText = "Erreur lors du traitement de la requête.";
        }
    } catch (err) {
        responseBox.innerText = `Erreur de connexion : ${err.message}`;
    }
}

async function runChunkingMethod(method) {
    const previewContainer = document.getElementById("chunks-preview-container");
    document.getElementById("chunk-method-title").innerText = method.replace("_", " ").toUpperCase();
    previewContainer.innerHTML = '<p class="text-muted"><i class="fa-solid fa-spinner fa-spin"></i> Découpage en cours...</p>';

    try {
        const res = await fetch(`${API_BASE}/chunking`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ method: method })
        });

        if (res.ok) {
            const data = await res.json();
            previewContainer.innerHTML = data.sample_chunks.map(c => `
                <div class="chunk-card">
                    <div class="chunk-card-header">
                        <span>Chunk #${c.id}</span>
                        <span>${c.length} chars</span>
                    </div>
                    <div class="chunk-card-text">${c.text.substring(0, 160)}...</div>
                </div>
            `).join("");

            fetchVectorialStatus();
            loadChunkingMetrics();
        }
    } catch (err) {
        previewContainer.innerHTML = `<p class="text-muted">Erreur: ${err.message}</p>`;
    }
}

async function loadChunkingMetrics() {
    try {
        const res = await fetch(`${API_BASE}/chunking/metrics`);
        if (res.ok) {
            const data = await res.json();
            const metrics = data.methods || data;
            const bestMethod = data.best_method || "Recursive Character Splitter";
            
            document.getElementById("best-chunk-method").innerText = bestMethod;

            const tbody = document.querySelector("#chunk-metrics-table tbody");

            tbody.innerHTML = Object.keys(metrics).map(m => `
                <tr style="${m === bestMethod ? 'background: #ecfdf5; font-weight: 600;' : ''}">
                    <td><strong>${m}</strong> ${m === bestMethod ? '🏆' : ''}</td>
                    <td>${metrics[m].count}</td>
                    <td>${metrics[m].avg_length} chars</td>
                    <td>± ${metrics[m].std_length}</td>
                    <td><span class="badge badge-success">${metrics[m].intra_similarity}</span></td>
                    <td>${metrics[m].inter_similarity}</td>
                    <td>${metrics[m].recall_at_k}</td>
                    <td>${metrics[m].precision_at_k}</td>
                    <td><span class="badge badge-api">${metrics[m].f1_score}</span></td>
                </tr>
            `).join("");

            renderChunkingCharts(metrics);
        }
    } catch (err) {
        console.warn("Chunk metrics error:", err);
    }
}

function renderChunkingCharts(data) {
    const labels = Object.keys(data);
    const intra = labels.map(l => data[l].intra_similarity);
    const inter = labels.map(l => data[l].inter_similarity);
    const f1 = labels.map(l => data[l].f1_score);

    const count = labels.map(l => data[l].count);
    const avgLen = labels.map(l => data[l].avg_length / 10);
    const stdLen = labels.map(l => data[l].std_length / 10);

    const ctx1 = document.getElementById("chunkingCoherenceChart").getContext("2d");
    if (chunkingCoherenceChartInstance) chunkingCoherenceChartInstance.destroy();
    
    chunkingCoherenceChartInstance = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Similarité Intra (Cohérence)', data: intra, backgroundColor: 'rgba(30, 58, 138, 0.85)' },
                { label: 'Similarité Inter (Redondance)', data: inter, backgroundColor: 'rgba(239, 68, 68, 0.65)' },
                { label: 'F1-score (Performance)', data: f1, backgroundColor: 'rgba(16, 185, 129, 0.85)' }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 1.0, grid: { color: '#e2e8f0' } },
                x: { grid: { color: '#e2e8f0' } }
            },
            plugins: { legend: { labels: { color: '#0f172a' } } }
        }
    });

    const ctx2 = document.getElementById("chunkingSizeChart").getContext("2d");
    if (chunkingSizeChartInstance) chunkingSizeChartInstance.destroy();

    chunkingSizeChartInstance = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Nb Chunks (Fragmentation)', data: count, backgroundColor: 'rgba(37, 99, 235, 0.75)' },
                { label: 'Long. Moyenne (/10)', data: avgLen, backgroundColor: 'rgba(2, 132, 199, 0.55)' },
                { label: 'Écart-type (/10)', data: stdLen, backgroundColor: 'rgba(245, 158, 11, 0.65)' }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, grid: { color: '#e2e8f0' } },
                x: { grid: { color: '#e2e8f0' } }
            },
            plugins: { legend: { labels: { color: '#0f172a' } } }
        }
    });
}

async function loadEmbeddingMetrics() {
    try {
        const res = await fetch(`${API_BASE}/embedding/metrics`);
        if (res.ok) {
            const data = await res.json();
            const metrics = data.methods || data;
            const bestMethod = data.best_method || "Sentence-BERT";

            document.getElementById("best-emb-method").innerText = bestMethod;

            const tbody = document.querySelector("#embedding-metrics-table tbody");

            tbody.innerHTML = Object.keys(metrics).map(m => `
                <tr style="${m === bestMethod ? 'background: #eff6ff; font-weight: 600;' : ''}">
                    <td><strong>${m}</strong> ${m === bestMethod ? '🏆' : ''}</td>
                    <td><span class="badge badge-api">${metrics[m].cosine_similarity}</span></td>
                    <td>${metrics[m].intra_similarity}</td>
                    <td>${metrics[m].inter_similarity}</td>
                    <td>${metrics[m].precision_at_k}</td>
                    <td>${metrics[m].recall_at_k}</td>
                    <td>${metrics[m].map}</td>
                    <td>${metrics[m].mrr}</td>
                    <td><span class="badge badge-success">${metrics[m].ndcg}</span></td>
                </tr>
            `).join("");

            renderEmbeddingComparisonChart(metrics);
        }
    } catch (err) {
        console.warn("Embedding metrics error:", err);
    }
}

function renderEmbeddingComparisonChart(data) {
    const ctx = document.getElementById("embeddingComparisonChart").getContext("2d");
    const methods = Object.keys(data);

    const cosine = methods.map(m => data[m].cosine_similarity);
    const precision = methods.map(m => data[m].precision_at_k);
    const recall = methods.map(m => data[m].recall_at_k);
    const mapScore = methods.map(m => data[m].map);
    const mrr = methods.map(m => data[m].mrr);
    const ndcg = methods.map(m => data[m].ndcg);

    if (embeddingChartInstance) embeddingChartInstance.destroy();

    embeddingChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: methods,
            datasets: [
                { label: 'Cosine Similarity', data: cosine, backgroundColor: 'rgba(30, 58, 138, 0.85)' },
                { label: 'Precision@k', data: precision, backgroundColor: 'rgba(2, 132, 199, 0.75)' },
                { label: 'Recall@k', data: recall, backgroundColor: 'rgba(37, 99, 235, 0.75)' },
                { label: 'MAP', data: mapScore, backgroundColor: 'rgba(16, 185, 129, 0.75)' },
                { label: 'MRR', data: mrr, backgroundColor: 'rgba(139, 92, 246, 0.75)' },
                { label: 'NDCG', data: ndcg, backgroundColor: 'rgba(245, 158, 11, 0.75)' }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 1.0, grid: { color: '#e2e8f0' } },
                x: { grid: { color: '#e2e8f0' } }
            },
            plugins: { legend: { labels: { color: '#0f172a' } } }
        }
    });
}

async function runRetrievalBenchmark() {
    const tbody = document.querySelector("#retrieval-metrics-table tbody");
    tbody.innerHTML = '<tr><td colspan="6" class="text-center"><i class="fa-solid fa-spinner fa-spin"></i> Évaluation des 6 méthodes de retrieval en cours...</td></tr>';

    try {
        const res = await fetch(`${API_BASE}/retrieval/metrics`);
        if (res.ok) {
            const data = await res.json();
            const metrics = data.methods || data;
            const bestMethod = data.best_method || "Re-ranking";

            document.getElementById("best-retrieval-method").innerText = bestMethod;

            tbody.innerHTML = Object.keys(metrics).map(m => `
                <tr style="${m === bestMethod ? 'background: #f3e8ff; font-weight: 600;' : ''}">
                    <td><strong>${m}</strong> ${m === bestMethod ? '🏆' : ''}</td>
                    <td>${metrics[m].precision_at_k}</td>
                    <td>${metrics[m].recall_at_k}</td>
                    <td><span class="badge badge-success">${metrics[m].mrr}</span></td>
                    <td>${metrics[m].ndcg}</td>
                    <td>${metrics[m].avg_latency_ms} ms</td>
                </tr>
            `).join("");

            if (metrics[bestMethod]) {
                document.getElementById("stat-best-mrr").innerText = metrics[bestMethod].mrr;
                document.getElementById("stat-ndcg").innerText = metrics[bestMethod].ndcg;
            }

            renderRetrievalChart(metrics);
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">Erreur: ${err.message}</td></tr>`;
    }
}

function renderRetrievalChart(data) {
    const ctx = document.getElementById("retrievalChart").getContext("2d");
    const methods = Object.keys(data);
    
    const precision = methods.map(m => data[m].precision_at_k);
    const recall = methods.map(m => data[m].recall_at_k);
    const mrr = methods.map(m => data[m].mrr);
    const ndcg = methods.map(m => data[m].ndcg);

    if (retrievalChartInstance) retrievalChartInstance.destroy();

    retrievalChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: methods,
            datasets: [
                { label: 'Precision@5', data: precision, backgroundColor: 'rgba(30, 58, 138, 0.85)' },
                { label: 'Recall@5', data: recall, backgroundColor: 'rgba(37, 99, 235, 0.75)' },
                { label: 'MRR', data: mrr, backgroundColor: 'rgba(16, 185, 129, 0.75)' },
                { label: 'NDCG@5', data: ndcg, backgroundColor: 'rgba(245, 158, 11, 0.75)' }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, max: 1.0, grid: { color: '#e2e8f0' } },
                x: { grid: { color: '#e2e8f0' } }
            },
            plugins: { legend: { labels: { color: '#0f172a' } } }
        }
    });
}
