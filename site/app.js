const DATA_URL = '../data/predictions.csv'; // Adjust path for GitHub Pages relative link
// Note: When deployed on GitHub Pages, the site is likely at root/site or using custom action to publish.
// The raw CSV is in data/predictions.csv in the repo.
// For a simple GH Pages deployment from /docs or /site, we need to make sure we can access the CSV.
// Often, raw content is accessed via: https://raw.githubusercontent.com/<user>/<repo>/main/data/predictions.csv
// Or relative if the whole repo is served (less common for Pages default).
// Let's assume we serve the whole repo or at least structure allows relative access.
// Ideally, the GH Action should copy data/*.csv to site/data/ for serving.
// BUT, the requirement says "Fetch CSV/JSON directly from repo".
// Let's use relative path assuming we run locally or with a setup that allows it. 
// If specific URL needed, we might need a config. 
// Let's try relative first mainly for local dev.
// PROD FIX: Use raw.githubusercontent.com for production reliability if simple relative fails due to folder structure.
// But for now, let's keep it relative to ../data/predictions.csv which works if we start server at repo root.
// If server started at site/, then ../data works.

function loadPredictions(callback) {
    Papa.parse(DATA_URL, {
        download: true,
        header: true,
        complete: function (results) {
            // Sort by target_date descending
            const data = results.data.filter(row => row.target_date); // Filter empty rows
            data.sort((a, b) => new Date(b.target_date) - new Date(a.target_date));
            callback(data);

            // Also update home if elements exist
            updateHome(data);
        }
    });
}

function updateHome(data) {
    const latest = data[0];
    if (!latest) return;

    const dateEl = document.getElementById('target-date');
    const priceEl = document.getElementById('predicted-price');
    const modelEl = document.getElementById('model-name');

    if (dateEl) dateEl.textContent = `Target: ${latest.target_date}`;
    if (priceEl) priceEl.textContent = `$${parseFloat(latest.predicted_close).toLocaleString()}`;
    if (modelEl) modelEl.textContent = `Model: ${latest.model_name}`;
}

function renderHistoryTable(data) {
    const tbody = document.querySelector('#history-table tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    data.forEach(row => {
        const tr = document.createElement('tr');

        const predicted = parseFloat(row.predicted_close).toFixed(2);
        const actual = row.actual_close ? parseFloat(row.actual_close).toFixed(2) : '-';
        const error = row.pct_error ? parseFloat(row.pct_error).toFixed(2) + '%' : '-';

        tr.innerHTML = `
            <td>${row.target_date}</td>
            <td>$${predicted}</td>
            <td>${actual !== '-' ? '$' + actual : actual}</td>
            <td>${error}</td>
            <td>${row.model_name}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderPerformanceChart(data) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    // Sort ascending for chart
    const chartData = [...data].reverse();

    const labels = chartData.map(d => d.target_date);
    const predicted = chartData.map(d => parseFloat(d.predicted_close));
    const actual = chartData.map(d => d.actual_close ? parseFloat(d.actual_close) : null);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Predicted',
                    data: predicted,
                    borderColor: '#f7931a',
                    tension: 0.1
                },
                {
                    label: 'Actual',
                    data: actual,
                    borderColor: '#c9d1d9',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    grid: { color: '#30363d' },
                    ticks: { color: '#8b949e' }
                },
                x: {
                    grid: { color: '#30363d' },
                    ticks: { color: '#8b949e' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#c9d1d9' }
                }
            }
        }
    });
}
