"""
Authentication routes — login, logout, and session management.
"""
from flask import Blueprint, request, session, redirect, url_for, render_template, flash, jsonify
from functools import wraps
from models.user import User

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorator to protect routes — redirects to login if not authenticated.
    Use this on any route that requires admin access.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # If API request, return JSON error
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Show the login page."""
    # If already logged in, go to dashboard
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    """Process login form submission."""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Please enter both email and password.', 'error')
        return redirect(url_for('auth.login_page'))

    # Look up the user
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Success — store user ID in session
        session['user_id'] = user.id
        session['user_email'] = user.email
        flash('Welcome back!', 'success')
        return redirect(url_for('auth.dashboard'))
    else:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.login_page'))


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/')
@login_required
def dashboard():
    """Main dashboard page (requires login)."""
    return render_template('dashboard.html')


@auth_bp.route('/inventory')
@login_required
def inventory_page():
    """Inventory management page."""
    return render_template('inventory.html')


@auth_bp.route('/sales')
@login_required
def sales_page():
    """Sales recording page."""
    return render_template('sales.html')


@auth_bp.route('/predictions')
@login_required
def predictions_page():
    """ML predictions page."""
    return render_template('predictions.html')
