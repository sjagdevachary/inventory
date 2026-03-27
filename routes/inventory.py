"""
Inventory routes — CRUD operations for products + CSV export.
"""
import csv
import io
from flask import Blueprint, request, jsonify, Response
from models import db
from models.product import Product
from routes.auth import login_required
from config import LOW_STOCK_THRESHOLD

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/api/products', methods=['GET'])
@login_required
def get_products():
    """Get all products."""
    products = Product.query.order_by(Product.name).all()
    return jsonify([p.to_dict() for p in products])


@inventory_bp.route('/api/products', methods=['POST'])
@login_required
def add_product():
    """Add a new product to inventory."""
    data = request.get_json()

    # Validate required fields
    required = ['name', 'category', 'price', 'quantity']
    for field in required:
        if field not in data or data[field] == '':
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        product = Product(
            name=data['name'].strip(),
            category=data['category'].strip(),
            price=float(data['price']),
            quantity=int(data['quantity'])
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully', 'product': product.to_dict()}), 201
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400


@inventory_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """Update an existing product."""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    try:
        if 'name' in data:
            product.name = data['name'].strip()
        if 'category' in data:
            product.category = data['category'].strip()
        if 'price' in data:
            product.price = float(data['price'])
        if 'quantity' in data:
            product.quantity = int(data['quantity'])

        db.session.commit()
        return jsonify({'message': 'Product updated', 'product': product.to_dict()})
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400


@inventory_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Delete a product from inventory."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Product "{product.name}" deleted'})


@inventory_bp.route('/api/products/low-stock', methods=['GET'])
@login_required
def low_stock_products():
    """Get products with quantity below the threshold."""
    threshold = request.args.get('threshold', LOW_STOCK_THRESHOLD, type=int)
    products = Product.query.filter(Product.quantity < threshold).order_by(Product.quantity).all()
    return jsonify({
        'threshold': threshold,
        'count': len(products),
        'products': [p.to_dict() for p in products]
    })


@inventory_bp.route('/api/products/export', methods=['GET'])
@login_required
def export_products_csv():
    """Download all products as a CSV file."""
    products = Product.query.order_by(Product.name).all()

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Category', 'Price', 'Quantity', 'Created At'])

    for p in products:
        writer.writerow([p.id, p.name, p.category, p.price, p.quantity, p.created_at.strftime('%Y-%m-%d')])

    # Return as downloadable CSV
    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=inventory_report.csv'}
    )
