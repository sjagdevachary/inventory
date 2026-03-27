/**
 * Sales Page JavaScript
 * Handles sales recording and sales history display
 */

document.addEventListener('DOMContentLoaded', () => {
    loadProductsDropdown();
    loadSalesHistory();
    // Set default date to today
    document.getElementById('saleDate').value = new Date().toISOString().split('T')[0];
});

// ── Load Products into Dropdown ────────────────────
async function loadProductsDropdown() {
    try {
        const res = await fetch('/api/products');
        const products = await res.json();

        const select = document.getElementById('saleProduct');
        select.innerHTML = '<option value="">Select product</option>';

        products.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = `${p.name} (Stock: ${p.quantity}) — $${p.price.toFixed(2)}`;
            if (p.quantity <= 0) option.disabled = true;
            select.appendChild(option);
        });
    } catch (err) {
        console.error('Failed to load products:', err);
    }
}

// ── Load Sales History ─────────────────────────────
async function loadSalesHistory() {
    try {
        const res = await fetch('/api/sales');
        const sales = await res.json();

        document.getElementById('salesCount').textContent = `${sales.length} records`;

        const tbody = document.getElementById('salesBody');

        if (sales.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="5">
                    <div class="empty-state">
                        <div class="empty-icon">💰</div>
                        <p>No sales recorded yet.</p>
                    </div>
                </td></tr>`;
            return;
        }

        tbody.innerHTML = sales.map(s => `
            <tr>
                <td style="color: var(--text-muted);">#${s.id}</td>
                <td style="font-weight: 600; color: var(--text-primary);">${s.product_name}</td>
                <td>${s.quantity_sold}</td>
                <td style="color: var(--accent-emerald); font-weight: 600;">$${s.revenue.toFixed(2)}</td>
                <td>${s.sale_date}</td>
            </tr>
        `).join('');
    } catch (err) {
        console.error('Failed to load sales:', err);
    }
}

// ── Record a Sale ──────────────────────────────────
async function recordSale(event) {
    event.preventDefault();

    const data = {
        product_id: parseInt(document.getElementById('saleProduct').value),
        quantity_sold: parseInt(document.getElementById('saleQuantity').value),
        sale_date: document.getElementById('saleDate').value
    };

    if (!data.product_id) {
        showNotification('Please select a product', 'error');
        return;
    }

    try {
        const res = await fetch('/api/sales', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            showNotification(`Sale recorded! ${result.remaining_stock} units remaining.`, 'success');
            document.getElementById('saleForm').reset();
            document.getElementById('saleDate').value = new Date().toISOString().split('T')[0];
            loadProductsDropdown();  // Refresh stock counts
            loadSalesHistory();      // Refresh table
        } else {
            showNotification(result.error || 'Failed to record sale', 'error');
        }
    } catch (err) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// ── Toast Notification ─────────────────────────────
function showNotification(message, type = 'info') {
    const existing = document.querySelector('.flash-messages');
    if (existing) existing.remove();

    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    const div = document.createElement('div');
    div.className = 'flash-messages';
    div.innerHTML = `<div class="flash ${type}">${icon} ${message}</div>`;
    document.body.appendChild(div);

    setTimeout(() => div.remove(), 3500);
}
