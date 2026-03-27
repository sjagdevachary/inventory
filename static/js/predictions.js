/**
 * Predictions Page JavaScript
 * Loads ML-powered demand predictions and restock suggestions
 */

document.addEventListener('DOMContentLoaded', loadPredictions);

// ── Load All Predictions ───────────────────────────
async function loadPredictions() {
    await Promise.all([
        loadRestockSuggestions(),
        loadProductPredictions()
    ]);
}

// ── Load Restock Suggestions ───────────────────────
async function loadRestockSuggestions() {
    try {
        const res = await fetch('/api/analytics/restock-suggestions');
        const suggestions = await res.json();

        // Count items needing restock
        const needsRestock = suggestions.filter(s => s.urgency !== 'low' && s.urgency !== 'unknown');
        document.getElementById('restockCount').textContent = `${needsRestock.length} items need attention`;

        const container = document.getElementById('restockList');

        if (suggestions.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No products to analyze.</p></div>';
            return;
        }

        container.innerHTML = suggestions.map(s => {
            const icons = {
                critical: '🔴', high: '🟠', medium: '🟡', low: '🟢', unknown: '⚪'
            };
            const icon = icons[s.urgency] || '⚪';

            let trendIcon = '';
            if (s.trend === 'increasing') trendIcon = '📈';
            else if (s.trend === 'decreasing') trendIcon = '📉';
            else if (s.trend === 'stable') trendIcon = '➡️';

            return `
                <div class="alert-item ${s.urgency}">
                    <span class="alert-icon">${icon}</span>
                    <div class="alert-body">
                        <div class="alert-title">
                            ${s.product_name}
                            ${s.confidence ? `<span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 8px;">${trendIcon} ${s.confidence}% confidence</span>` : ''}
                        </div>
                        <div class="alert-description">${s.suggestion}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 700; font-size: 0.9rem;">${s.current_stock} in stock</div>
                        ${s.restock_quantity > 0 
                            ? `<span class="badge badge-warning">Restock: +${s.restock_quantity}</span>` 
                            : '<span class="badge badge-success">OK</span>'}
                    </div>
                </div>`;
        }).join('');
    } catch (err) {
        console.error('Failed to load restock suggestions:', err);
        document.getElementById('restockList').innerHTML = '<div class="empty-state"><p>❌ Failed to load suggestions</p></div>';
    }
}

// ── Load Per-Product Predictions ───────────────────
async function loadProductPredictions() {
    try {
        // First get all products
        const prodRes = await fetch('/api/products');
        const products = await prodRes.json();

        const days = document.getElementById('predictionDays').value;
        const grid = document.getElementById('predictionGrid');

        // Fetch predictions in parallel
        const predictions = await Promise.all(
            products.map(async (p) => {
                const res = await fetch(`/api/analytics/predict/${p.id}?days=${days}`);
                return await res.json();
            })
        );

        if (predictions.length === 0) {
            grid.innerHTML = '<div class="empty-state" style="grid-column: 1/-1;"><p>No products to predict demand for.</p></div>';
            return;
        }

        grid.innerHTML = predictions.map(pred => {
            if (!pred.success) {
                return `
                    <div class="prediction-card">
                        <div class="prediction-header">
                            <span class="prediction-product">${pred.product_name || 'Unknown'}</span>
                            <span class="badge badge-info">⚪ No data</span>
                        </div>
                        <div class="empty-state" style="padding: 16px;">
                            <p>${pred.message || 'Not enough sales data for prediction'}</p>
                        </div>
                    </div>`;
            }

            const trendColors = {
                increasing: 'var(--accent-emerald)',
                decreasing: 'var(--accent-rose)',
                stable: 'var(--accent-cyan)'
            };
            const trendIcons = { increasing: '📈', decreasing: '📉', stable: '➡️' };
            const trendColor = trendColors[pred.trend] || 'var(--text-secondary)';

            // Weekly breakdown bars
            const maxWeekly = Math.max(...pred.weekly_demand.map(w => w.predicted_quantity), 1);
            const weeklyBars = pred.weekly_demand.map(w => {
                const pct = (w.predicted_quantity / maxWeekly) * 100;
                return `
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="font-size: 0.7rem; color: var(--text-muted); width: 45px;">Wk ${w.week}</span>
                        <div style="flex: 1; background: rgba(255,255,255,0.05); border-radius: 4px; height: 16px; overflow: hidden;">
                            <div style="width: ${pct}%; height: 100%; background: var(--gradient-primary); border-radius: 4px; transition: width 0.5s ease;"></div>
                        </div>
                        <span style="font-size: 0.75rem; font-weight: 600; width: 30px; text-align: right;">${w.predicted_quantity}</span>
                    </div>`;
            }).join('');

            return `
                <div class="prediction-card">
                    <div class="prediction-header">
                        <span class="prediction-product">${pred.product_name}</span>
                        <span class="badge badge-${pred.confidence > 50 ? 'success' : 'warning'}">${pred.confidence}% conf.</span>
                    </div>

                    <div class="prediction-stats">
                        <div class="prediction-stat">
                            <div class="stat-value" style="color: var(--primary-light);">${pred.total_predicted_demand}</div>
                            <div class="stat-label">Predicted Demand</div>
                        </div>
                        <div class="prediction-stat">
                            <div class="stat-value">${pred.daily_average}</div>
                            <div class="stat-label">Daily Average</div>
                        </div>
                        <div class="prediction-stat">
                            <div class="stat-value">${pred.current_stock}</div>
                            <div class="stat-label">Current Stock</div>
                        </div>
                        <div class="prediction-stat">
                            <div class="stat-value" style="color: ${trendColor};">${trendIcons[pred.trend]} ${pred.trend}</div>
                            <div class="stat-label">Trend</div>
                        </div>
                    </div>

                    <div style="margin-bottom: 8px; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary);">Weekly Forecast</div>
                    ${weeklyBars}
                </div>`;
        }).join('');
    } catch (err) {
        console.error('Failed to load predictions:', err);
        document.getElementById('predictionGrid').innerHTML = '<div class="empty-state" style="grid-column:1/-1;"><p>❌ Failed to load predictions</p></div>';
    }
}
