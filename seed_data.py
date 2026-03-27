"""
Seed Data Script — Populates the database with sample data.

Run this once to create:
- An admin user account
- 12 sample products across categories
- ~200 realistic sales records over 3 months

Usage: python seed_data.py
"""
import random
from datetime import datetime, timedelta
from app import create_app
from models import db
from models.user import User
from models.product import Product
from models.sale import Sale


def seed_database():
    """Populate database with sample data for demonstration."""
    app = create_app()

    with app.app_context():
        # Clear existing data
        print("🗑️  Clearing existing data...")
        Sale.query.delete()
        Product.query.delete()
        User.query.delete()
        db.session.commit()

        # ── 1. Create Admin User ──────────────────────────────
        print("👤 Creating admin user...")
        admin = User(email='admin@inventory.com')
        admin.set_password('admin123')
        db.session.add(admin)

        # ── 2. Create Products ────────────────────────────────
        print("📦 Adding sample products...")
        products_data = [
            # Electronics
            {'name': 'Wireless Mouse', 'category': 'Electronics', 'price': 29.99, 'quantity': 45},
            {'name': 'USB-C Hub', 'category': 'Electronics', 'price': 49.99, 'quantity': 30},
            {'name': 'Bluetooth Speaker', 'category': 'Electronics', 'price': 79.99, 'quantity': 8},  # Low stock
            {'name': 'Webcam HD', 'category': 'Electronics', 'price': 59.99, 'quantity': 22},
            # Clothing
            {'name': 'Cotton T-Shirt', 'category': 'Clothing', 'price': 19.99, 'quantity': 120},
            {'name': 'Denim Jeans', 'category': 'Clothing', 'price': 49.99, 'quantity': 5},  # Low stock
            {'name': 'Running Shoes', 'category': 'Clothing', 'price': 89.99, 'quantity': 35},
            # Food & Beverage
            {'name': 'Organic Coffee Beans', 'category': 'Food', 'price': 14.99, 'quantity': 60},
            {'name': 'Protein Bars (Box)', 'category': 'Food', 'price': 24.99, 'quantity': 3},  # Low stock
            {'name': 'Green Tea (50 bags)', 'category': 'Food', 'price': 9.99, 'quantity': 80},
            # Office Supplies
            {'name': 'Notebook Set', 'category': 'Office', 'price': 12.99, 'quantity': 95},
            {'name': 'Ergonomic Pen Pack', 'category': 'Office', 'price': 8.99, 'quantity': 150},
        ]

        products = []
        for pdata in products_data:
            p = Product(**pdata)
            products.append(p)
            db.session.add(p)

        db.session.commit()

        # ── 3. Generate Sales Records ─────────────────────────
        print("📈 Generating 3 months of sales data...")
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=90)

        sales_count = 0
        current_date = start_date

        while current_date <= end_date:
            # Generate 1-4 sales per day
            num_sales = random.randint(1, 4)
            for _ in range(num_sales):
                product = random.choice(products)

                # Vary quantity sold (some products sell more)
                if product.category == 'Clothing':
                    qty = random.randint(1, 5)
                elif product.category == 'Food':
                    qty = random.randint(2, 8)
                elif product.category == 'Electronics':
                    qty = random.randint(1, 3)
                else:
                    qty = random.randint(1, 6)

                sale = Sale(
                    product_id=product.id,
                    quantity_sold=qty,
                    sale_date=current_date,
                    revenue=round(product.price * qty, 2)
                )
                db.session.add(sale)
                sales_count += 1

            current_date += timedelta(days=1)

        db.session.commit()

        # ── Summary ───────────────────────────────────────────
        print(f"\n✅ Database seeded successfully!")
        print(f"   👤 Admin: admin@inventory.com / admin123")
        print(f"   📦 Products: {len(products)}")
        print(f"   📈 Sales records: {sales_count}")
        print(f"   📅 Date range: {start_date} → {end_date}")


if __name__ == '__main__':
    seed_database()
