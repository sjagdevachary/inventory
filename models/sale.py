"""
Sale model for tracking sales records.
"""
from models import db
from datetime import datetime

class Sale(db.Model):
    """A record of a product sale."""
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    revenue = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'quantity_sold': self.quantity_sold,
            'sale_date': self.sale_date.strftime('%Y-%m-%d'),
            'revenue': self.revenue
        }

    def __repr__(self):
        return f'<Sale {self.product_id} x{self.quantity_sold}>'
