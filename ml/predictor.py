"""
Demand Predictor using Linear Regression.
Predicts future product demand based on historical sales data.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta


def predict_demand(sales_data, days_ahead=30):
    """
    Predict future demand for a product using Linear Regression.
    
    Args:
        sales_data: List of dicts with 'sale_date' and 'quantity_sold'
        days_ahead: Number of days to predict into the future
    
    Returns:
        dict with prediction results and model info
    """
    if not sales_data or len(sales_data) < 3:
        return {
            'success': False,
            'message': 'Not enough sales data (need at least 3 records)',
            'predicted_demand': 0,
            'confidence': 0
        }

    # Convert to DataFrame
    df = pd.DataFrame(sales_data)
    df['sale_date'] = pd.to_datetime(df['sale_date'])

    # Aggregate daily sales (sum quantities per day)
    daily_sales = df.groupby('sale_date')['quantity_sold'].sum().reset_index()
    daily_sales = daily_sales.sort_values('sale_date')

    # Create numeric feature: days since first sale
    first_date = daily_sales['sale_date'].min()
    daily_sales['day_number'] = (daily_sales['sale_date'] - first_date).dt.days

    # Prepare features (X) and target (y)
    X = daily_sales['day_number'].values.reshape(-1, 1)  # 2D array for sklearn
    y = daily_sales['quantity_sold'].values

    # Train Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Calculate R² score (model confidence)
    r2_score = model.score(X, y)

    # Predict for future days
    last_day = daily_sales['day_number'].max()
    future_days = np.array([last_day + i for i in range(1, days_ahead + 1)]).reshape(-1, 1)
    predictions = model.predict(future_days)

    # Ensure predictions are non-negative
    predictions = np.maximum(predictions, 0)

    # Calculate total predicted demand and daily average
    total_predicted = int(np.sum(predictions))
    daily_average = round(float(np.mean(predictions)), 1)

    # Generate prediction points for charting
    last_date = daily_sales['sale_date'].max()
    prediction_points = []
    for i, pred in enumerate(predictions):
        future_date = last_date + timedelta(days=i + 1)
        prediction_points.append({
            'date': future_date.strftime('%Y-%m-%d'),
            'predicted_quantity': round(float(pred), 1)
        })

    # Weekly breakdown
    weekly_demand = []
    for week in range(0, days_ahead, 7):
        week_slice = predictions[week:week + 7]
        weekly_demand.append({
            'week': week // 7 + 1,
            'predicted_quantity': int(np.sum(week_slice))
        })

    return {
        'success': True,
        'total_predicted_demand': total_predicted,
        'daily_average': daily_average,
        'days_ahead': days_ahead,
        'confidence': round(max(r2_score * 100, 0), 1),  # as percentage
        'trend': 'increasing' if model.coef_[0] > 0.01 else ('decreasing' if model.coef_[0] < -0.01 else 'stable'),
        'slope': round(float(model.coef_[0]), 4),
        'prediction_points': prediction_points,
        'weekly_demand': weekly_demand
    }


def get_restock_suggestion(product, sales_data, days_ahead=30):
    """
    Suggest restock quantity based on prediction and current stock.
    
    Args:
        product: Product dict with 'quantity' and 'name'
        sales_data: Historical sales data for the product
        days_ahead: Planning horizon in days
    
    Returns:
        dict with restock recommendations
    """
    prediction = predict_demand(sales_data, days_ahead)

    if not prediction['success']:
        return {
            'product_name': product['name'],
            'current_stock': product['quantity'],
            'suggestion': 'Not enough data to predict',
            'restock_quantity': 0,
            'urgency': 'unknown'
        }

    predicted_demand = prediction['total_predicted_demand']
    current_stock = product['quantity']
    deficit = predicted_demand - current_stock

    # Determine urgency level
    if current_stock <= 0:
        urgency = 'critical'
        suggestion = f'OUT OF STOCK! Restock immediately. Predicted demand: {predicted_demand} units in {days_ahead} days.'
    elif deficit > predicted_demand * 0.8:
        urgency = 'high'
        suggestion = f'Stock will run out soon. Restock {deficit} units to meet {days_ahead}-day demand.'
    elif deficit > 0:
        urgency = 'medium'
        suggestion = f'Stock may be insufficient. Consider restocking {deficit} units.'
    else:
        urgency = 'low'
        suggestion = f'Stock is sufficient for the next {days_ahead} days.'

    # Add a safety buffer of 20% for restock
    restock_quantity = max(0, int(deficit * 1.2))

    return {
        'product_name': product['name'],
        'current_stock': current_stock,
        'predicted_demand': predicted_demand,
        'restock_quantity': restock_quantity,
        'suggestion': suggestion,
        'urgency': urgency,
        'confidence': prediction['confidence'],
        'trend': prediction['trend']
    }
