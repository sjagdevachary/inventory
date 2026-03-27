"""
Analytics routes — sales trends, product performance, and ML predictions.
"""
from flask import Blueprint, request, jsonify
from models import db
from models.product import Product
from models.sale import Sale
from routes.auth import login_required
from ml.predictor import predict_demand, get_restock_suggestion
from sqlalchemy import func
from config import LOW_STOCK_THRESHOLD

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics/summary', methods=['GET'])
@login_required
def get_summary():
    """Get dashboard KPI summary."""
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.quantity < LOW_STOCK_THRESHOLD).count()
    total_sales = db.session.query(func.count(Sale.id)).scalar() or 0
    total_revenue = db.session.query(func.sum(Sale.revenue)).scalar() or 0
    total_items_sold = db.session.query(func.sum(Sale.quantity_sold)).scalar() or 0

    return jsonify({
        'total_products': total_products,
        'low_stock_count': low_stock,
        'total_sales': total_sales,
        'total_revenue': round(total_revenue, 2),
        'total_items_sold': total_items_sold
    })


@analytics_bp.route('/api/analytics/sales-trends', methods=['GET'])
@login_required
def sales_trends():
    """
    Get aggregated sales over time for line chart.
    Groups sales by date and returns daily totals.
    """
    results = db.session.query(
        Sale.sale_date,
        func.sum(Sale.quantity_sold).label('total_quantity'),
        func.sum(Sale.revenue).label('total_revenue')
    ).group_by(Sale.sale_date).order_by(Sale.sale_date).all()

    trends = [{
        'date': row.sale_date.strftime('%Y-%m-%d'),
        'quantity': int(row.total_quantity),
        'revenue': round(float(row.total_revenue), 2)
    } for row in results]

    return jsonify(trends)


@analytics_bp.route('/api/analytics/product-performance', methods=['GET'])
@login_required
def product_performance():
    """
    Get total sales by product for bar chart.
    """
    results = db.session.query(
        Product.name,
        func.sum(Sale.quantity_sold).label('total_sold'),
        func.sum(Sale.revenue).label('total_revenue')
    ).join(Sale).group_by(Product.id).order_by(func.sum(Sale.revenue).desc()).all()

    performance = [{
        'product_name': row.name,
        'total_sold': int(row.total_sold),
        'total_revenue': round(float(row.total_revenue), 2)
    } for row in results]

    return jsonify(performance)


@analytics_bp.route('/api/analytics/predict/<int:product_id>', methods=['GET'])
@login_required
def predict_product_demand(product_id):
    """
    Predict future demand for a specific product using ML.
    Query param: days (default 30)
    """
    product = Product.query.get_or_404(product_id)
    days = request.args.get('days', 30, type=int)

    # Get historical sales for this product
    sales = Sale.query.filter_by(product_id=product_id).order_by(Sale.sale_date).all()
    sales_data = [{'sale_date': s.sale_date.strftime('%Y-%m-%d'), 'quantity_sold': s.quantity_sold} for s in sales]

    # Run prediction
    prediction = predict_demand(sales_data, days_ahead=days)
    prediction['product_name'] = product.name
    prediction['current_stock'] = product.quantity

    return jsonify(prediction)


@analytics_bp.route('/api/analytics/restock-suggestions', methods=['GET'])
@login_required
def restock_suggestions():
    """
    Get smart restock suggestions for all products.
    Uses ML predictions to recommend restocking quantities.
    """
    products = Product.query.all()
    suggestions = []

    for product in products:
        # Get sales data for this product
        sales = Sale.query.filter_by(product_id=product.id).order_by(Sale.sale_date).all()
        sales_data = [{'sale_date': s.sale_date.strftime('%Y-%m-%d'), 'quantity_sold': s.quantity_sold} for s in sales]

        suggestion = get_restock_suggestion(product.to_dict(), sales_data)
        suggestion['product_id'] = product.id
        suggestions.append(suggestion)

    # Sort by urgency: critical > high > medium > low > unknown
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
    suggestions.sort(key=lambda x: urgency_order.get(x['urgency'], 5))

    return jsonify(suggestions)
