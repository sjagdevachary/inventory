"""
Sales routes — record sales and list sales history.
"""
from flask import Blueprint, request, jsonify
from models import db
from models.product import Product
from models.sale import Sale
from routes.auth import login_required
from datetime import datetime

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/api/sales', methods=['GET'])
@login_required
def get_sales():
    """Get all sales records, newest first."""
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return jsonify([s.to_dict() for s in sales])


@sales_bp.route('/api/sales', methods=['POST'])
@login_required
def add_sale():
    """
    Record a new sale.
    Automatically decrements the product's stock quantity.
    """
    data = request.get_json()

    # Validate required fields
    required = ['product_id', 'quantity_sold']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        product_id = int(data['product_id'])
        quantity_sold = int(data['quantity_sold'])

        if quantity_sold <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400

        # Find the product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check if enough stock is available
        if product.quantity < quantity_sold:
            return jsonify({
                'error': f'Insufficient stock. Available: {product.quantity}, Requested: {quantity_sold}'
            }), 400

        # Parse sale date (default to today)
        sale_date_str = data.get('sale_date', datetime.utcnow().strftime('%Y-%m-%d'))
        sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date()

        # Calculate revenue
        revenue = product.price * quantity_sold

        # Create sale record
        sale = Sale(
            product_id=product_id,
            quantity_sold=quantity_sold,
            sale_date=sale_date,
            revenue=revenue
        )

        # Decrement stock
        product.quantity -= quantity_sold

        db.session.add(sale)
        db.session.commit()

        return jsonify({
            'message': 'Sale recorded successfully',
            'sale': sale.to_dict(),
            'remaining_stock': product.quantity
        }), 201

    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
