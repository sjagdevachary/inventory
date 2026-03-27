"""
Smart Inventory Management System — Flask Application Entry Point.

This is the main file that creates and configures the Flask app,
registers all routes, and starts the server.
"""
from flask import Flask
from models import db
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY

def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    # Initialize database
    db.init_app(app)

    # Register blueprints (route modules)
    from routes.auth import auth_bp
    from routes.inventory import inventory_bp
    from routes.sales import sales_bp
    from routes.analytics import analytics_bp
    from routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(chatbot_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


# Run the app
if __name__ == '__main__':
    app = create_app()
    print("\n🚀 Smart Inventory Management System")
    print("   Running at: http://127.0.0.1:5000")
    print("   Admin Login: admin@inventory.com / admin123\n")
    app.run(debug=True, port=5000)
