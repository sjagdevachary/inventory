/**
 * Dashboard Page JavaScript
 * Loads KPIs, renders charts, and shows low-stock alerts
 */

// Chart.js global config for dark theme
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';
Chart.defaults.font.family = 'Inter';

document.addEventListener('DOMContentLoaded', () => {
    loadSummary();
    loadSalesTrend();
    loadProductPerformance();
    loadLowStockAlerts();
});

// ── Load KPI Summary ───────────────────────────────
async function loadSummary() {
    try {
        const res = await fetch('/api/analytics/summary');
        const data = await res.json();

        document.getElementById('kpiProducts').textContent = data.total_products;
        document.getElementById('kpiLowStock').textContent = data.low_stock_count;
        document.getElementById('kpiSales').textContent = data.total_items_sold.toLocaleString();
        document.getElementById('kpiRevenue').textContent = '$' + data.total_revenue.toLocaleString();
    } catch (err) {
        console.error('Failed to load summary:', err);
    }
}

// ── Sales Trend Line Chart ─────────────────────────
async function loadSalesTrend() {
    try {
        const res = await fetch('/api/analytics/sales-trends');
        const data = await res.json();

        // Aggregate weekly for cleaner chart
        const weekly = aggregateWeekly(data);

        const ctx = document.getElementById('salesTrendChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: weekly.map(d => d.label),
                datasets: [
                    {
                        label: 'Revenue ($)',
                        data: weekly.map(d => d.revenue),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        borderWidth: 2
                    },
                    {
                        label: 'Quantity Sold',
                        data: weekly.map(d => d.quantity),
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.05)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        borderWidth: 2,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Revenue ($)' },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: { display: true, text: 'Quantity' },
                        grid: { display: false }
                    },
                    x: {
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load sales trend:', err);
    }
}

// ── Product Performance Bar Chart ──────────────────
async function loadProductPerformance() {
    try {
        const res = await fetch('/api/analytics/product-performance');
        const data = await res.json();

        // Color palette for bars
        const colors = [
            '#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444',
            '#a855f7', '#ec4899', '#14b8a6', '#f97316', '#8b5cf6',
            '#06b6d4', '#84cc16'
        ];

        const ctx = document.getElementById('productPerformanceChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.product_name),
                datasets: [{
                    label: 'Total Revenue ($)',
                    data: data.map(d => d.total_revenue),
                    backgroundColor: data.map((_, i) => colors[i % colors.length] + '40'),
                    borderColor: data.map((_, i) => colors[i % colors.length]),
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Revenue ($)' },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { maxRotation: 45 }
                    }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load product performance:', err);
    }
}

// ── Low Stock Alerts ───────────────────────────────
async function loadLowStockAlerts() {
    try {
        const res = await fetch('/api/products/low-stock');
        const data = await res.json();

        document.getElementById('alertCount').textContent = data.count + ' items';

        const container = document.getElementById('alertsList');

        if (data.count === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">✅</div>
                    <p>All products are well-stocked!</p>
                </div>`;
            return;
        }

        container.innerHTML = data.products.map(p => {
            const urgency = p.quantity <= 3 ? 'critical' : (p.quantity <= 5 ? 'high' : 'medium');
            const icon = urgency === 'critical' ? '🔴' : (urgency === 'high' ? '🟠' : '🟡');
            return `
                <div class="alert-item ${urgency}">
                    <span class="alert-icon">${icon}</span>
                    <div class="alert-body">
                        <div class="alert-title">${p.name}</div>
                        <div class="alert-description">Only ${p.quantity} units left — ${p.category}</div>
                    </div>
                    <span class="badge badge-${urgency === 'critical' ? 'danger' : 'warning'}">${p.quantity} left</span>
                </div>`;
        }).join('');
    } catch (err) {
        console.error('Failed to load alerts:', err);
    }
}

// ── Helper: aggregate daily data into weekly buckets ─
function aggregateWeekly(dailyData) {
    const weeks = [];
    for (let i = 0; i < dailyData.length; i += 7) {
        const chunk = dailyData.slice(i, i + 7);
        const lastDate = chunk[chunk.length - 1].date;
        weeks.push({
            label: lastDate.substring(5),  // MM-DD format
            quantity: chunk.reduce((sum, d) => sum + d.quantity, 0),
            revenue: Math.round(chunk.reduce((sum, d) => sum + d.revenue, 0) * 100) / 100
        });
    }
    return weeks;
}
