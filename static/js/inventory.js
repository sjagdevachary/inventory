/**
 * Inventory Page JavaScript
 * Handles product CRUD operations via fetch API
 */

let allProducts = [];  // Store for client-side filtering

document.addEventListener('DOMContentLoaded', loadProducts);

// ── Load Products ──────────────────────────────────
async function loadProducts() {
    try {
        const res = await fetch('/api/products');
        allProducts = await res.json();
        renderProducts(allProducts);
    } catch (err) {
        console.error('Failed to load products:', err);
        document.getElementById('productsBody').innerHTML = `
            <tr><td colspan="7" class="empty-state">❌ Failed to load products</td></tr>`;
    }
}

// ── Render Products Table ──────────────────────────
function renderProducts(products) {
    const tbody = document.getElementById('productsBody');

    if (products.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="7">
                <div class="empty-state">
                    <div class="empty-icon">📦</div>
                    <p>No products found. Add your first product!</p>
                </div>
            </td></tr>`;
        return;
    }

    tbody.innerHTML = products.map(p => {
        // Determine stock status badge
        let statusBadge;
        if (p.quantity <= 3) {
            statusBadge = '<span class="badge badge-danger">🔴 Critical</span>';
        } else if (p.quantity < 10) {
            statusBadge = '<span class="badge badge-warning">🟡 Low</span>';
        } else {
            statusBadge = '<span class="badge badge-success">🟢 In Stock</span>';
        }

        return `
            <tr>
                <td style="color: var(--text-muted);">#${p.id}</td>
                <td style="font-weight: 600; color: var(--text-primary);">${p.name}</td>
                <td><span class="badge badge-info">${p.category}</span></td>
                <td>$${p.price.toFixed(2)}</td>
                <td style="font-weight: 600;">${p.quantity}</td>
                <td>${statusBadge}</td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-ghost btn-sm" onclick="openEditModal(${p.id})" title="Edit">✏️</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteProduct(${p.id}, '${p.name}')" title="Delete">🗑️</button>
                    </div>
                </td>
            </tr>`;
    }).join('');
}

// ── Filter Products (Search) ───────────────────────
function filterProducts() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const filtered = allProducts.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.category.toLowerCase().includes(query)
    );
    renderProducts(filtered);
}

// ── Open Add Modal ─────────────────────────────────
function openAddModal() {
    document.getElementById('modalTitle').textContent = 'Add Product';
    document.getElementById('productId').value = '';
    document.getElementById('productForm').reset();
    document.getElementById('productModal').classList.add('show');
}

// ── Open Edit Modal ────────────────────────────────
function openEditModal(id) {
    const product = allProducts.find(p => p.id === id);
    if (!product) return;

    document.getElementById('modalTitle').textContent = 'Edit Product';
    document.getElementById('productId').value = product.id;
    document.getElementById('productName').value = product.name;
    document.getElementById('productCategory').value = product.category;
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productQuantity').value = product.quantity;
    document.getElementById('productModal').classList.add('show');
}

// ── Close Modal ────────────────────────────────────
function closeModal() {
    document.getElementById('productModal').classList.remove('show');
}

// ── Save Product (Add or Update) ───────────────────
async function saveProduct(event) {
    event.preventDefault();

    const id = document.getElementById('productId').value;
    const data = {
        name: document.getElementById('productName').value,
        category: document.getElementById('productCategory').value,
        price: parseFloat(document.getElementById('productPrice').value),
        quantity: parseInt(document.getElementById('productQuantity').value)
    };

    try {
        const url = id ? `/api/products/${id}` : '/api/products';
        const method = id ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            closeModal();
            loadProducts();  // Refresh the table
            showNotification(result.message || 'Product saved!', 'success');
        } else {
            showNotification(result.error || 'Failed to save product', 'error');
        }
    } catch (err) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// ── Delete Product ─────────────────────────────────
async function deleteProduct(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
        const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
        const result = await res.json();

        if (res.ok) {
            loadProducts();
            showNotification(result.message, 'success');
        } else {
            showNotification(result.error || 'Failed to delete', 'error');
        }
    } catch (err) {
        showNotification('Network error. Please try again.', 'error');
    }
}

// ── Toast Notification ─────────────────────────────
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.flash-messages');
    if (existing) existing.remove();

    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    const div = document.createElement('div');
    div.className = 'flash-messages';
    div.innerHTML = `<div class="flash ${type}">${icon} ${message}</div>`;
    document.body.appendChild(div);

    setTimeout(() => div.remove(), 3500);
}

// Close modal when clicking outside
document.getElementById('productModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});
