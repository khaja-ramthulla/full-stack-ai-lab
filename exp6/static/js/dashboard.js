let charts = {};

document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();
    predictionForm.addEventListener("submit", handlePrediction);
    clearHistory.addEventListener("click", clearHistoryFn);
    setInterval(loadDashboardData, 30000);
});

/* LOAD DASHBOARD */
async function loadDashboardData() {
    const res = await fetch("/api/stats");
    const data = await res.json();

    updateStats(data);
    updateCharts(data);
    updateRecent(data.recent_predictions);
}

/* STATS */
function updateStats(data) {
    totalPredictions.innerText = data.total_predictions || 0;

    if (data.avg_confidence_by_model?.length) {
        const avg =
            data.avg_confidence_by_model.reduce(
                (s, x) => s + x.avg_confidence, 0
            ) / data.avg_confidence_by_model.length;
        avgConfidence.innerText = (avg * 100).toFixed(1) + "%";
    }

    modelsUsed.innerText = data.predictions_by_model.length;

    if (data.predictions_by_class.length) {
        const top = data.predictions_by_class.reduce(
            (a, b) => b.count > a.count ? b : a
        );
        topPrediction.innerText = top._id;
    }
}

/* CHARTS */
function updateCharts(data) {

    // Predictions by Species
    renderChart(
        "predictionsByClass",
        "bar",
        data.predictions_by_class.map(x => x._id),
        data.predictions_by_class.map(x => x.count),
        ["#7c83fd", "#a084dc", "#f2b5d4"]
    );

    // Predictions by Model
    renderChart(
        "predictionsByModel",
        "doughnut",
        data.predictions_by_model.map(x => format(x._id)),
        data.predictions_by_model.map(x => x.count),
        ["#7c83fd", "#a084dc"]
    );

    // Confidence Distribution
    renderChart(
        "confidenceDistribution",
        "pie",
        data.confidence_distribution.map(x => x._id),
        data.confidence_distribution.map(x => x.count),
        ["#4caf50", "#ffc107", "#f44336"]
    );

    // Model Performance: LR vs NB
    const modelPerf = {
        logistic_regression: 0,
        naive_bayes: 0
    };

    data.avg_confidence_by_model.forEach(m => {
        modelPerf[m._id] = (m.avg_confidence * 100).toFixed(2);
    });

    renderChart(
        "modelComparison",
        "bar",
        ["Logistic Regression", "Naive Bayes"],
        [modelPerf.logistic_regression, modelPerf.naive_bayes],
        ["#7c83fd", "#a084dc"]
    );
}

/* CHART RENDER */
function renderChart(id, type, labels, values, colors) {
    if (charts[id]) charts[id].destroy();

    charts[id] = new Chart(document.getElementById(id), {
        type,
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: type !== "bar", position: "bottom" }
            },
            scales: type === "bar" ? {
                y: { beginAtZero: true }
            } : {}
        }
    });
}

/* RECENT */
function updateRecent(list) {
    recentPredictionsList.innerHTML = "";

    if (!list.length) {
        recentPredictionsList.innerHTML =
            "<p style='text-align:center;color:#777'>No predictions yet</p>";
        return;
    }

    list.forEach(p => {
        const row = document.createElement("div");
        row.className = "prediction-row";

        const time = new Date(
            p.timestamp.$date || p.timestamp
        ).toLocaleString();

        row.innerHTML = `
            <span>${time}</span>
            <span class="bold">${p.prediction}</span>
            <span>${format(p.model)}</span>
            <span class="confidence">${(p.confidence * 100).toFixed(1)}%</span>
        `;
        recentPredictionsList.appendChild(row);
    });
}

/* PREDICT */
async function handlePrediction(e) {
    e.preventDefault();

    const features = [
        +sepal_length.value,
        +sepal_width.value,
        +petal_length.value,
        +petal_width.value
    ];

    const model = document.getElementById("model").value;

    const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ features, model })
    });

    const data = await res.json();

    // Show output box
    predictionResult.style.display = "block";
    resPrediction.innerText = data.prediction.toUpperCase();
    resConfidence.innerText = (data.confidence * 100).toFixed(2) + "%";
    resModel.innerText = data.model_used.replace("_", " ");

    loadDashboardData();
}

/* CLEAR */
async function clearHistoryFn() {
    const res = await fetch("/api/clear-history", { method: "POST" });
    const data = await res.json();
    alert(`Cleared ${data.deleted_count} records`);
    loadDashboardData();
}

function format(text) {
    return text.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase());
}
