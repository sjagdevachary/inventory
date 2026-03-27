"""
Chatbot route — simple rule-based chatbot for inventory queries.
"""
from flask import Blueprint, request, jsonify
from models.product import Product
from models.sale import Sale
from models import db
from sqlalchemy import func
from config import LOW_STOCK_THRESHOLD

chatbot_bp = Blueprint('chatbot', __name__)

# Keyword-based responses
GREETINGS = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
FAREWELLS = ['bye', 'goodbye', 'thanks', 'thank you']


@chatbot_bp.route('/api/chatbot', methods=['POST'])
def chat():
    """
    Process a chatbot message and return a rule-based response.
    Understands queries about stock, sales, products, and help.
    """
    data = request.get_json()
    message = data.get('message', '').strip().lower()

    if not message:
        return jsonify({'response': "I didn't catch that. Could you try again?"})

    response = generate_response(message)
    return jsonify({'response': response})


def generate_response(message):
    """Generate a response based on keyword matching."""

    # Greetings
    if any(word in message for word in GREETINGS):
        return "👋 Hello! I'm your Inventory Assistant. I can help you with:\n• Stock levels\n• Low stock alerts\n• Sales information\n• Product searches\n\nTry asking: 'Show low stock' or 'How many products do we have?'"

    # Farewells
    if any(word in message for word in FAREWELLS):
        return "👋 Goodbye! Feel free to ask me anything anytime."

    # Help
    if 'help' in message or 'what can you do' in message:
        return ("🤖 I can help you with:\n"
                "• **'low stock'** — Show products with low stock\n"
                "• **'total products'** — Count of all products\n"
                "• **'total sales'** — Total sales revenue\n"
                "• **'search [product name]'** — Find a product\n"
                "• **'top products'** — Best-selling products\n"
                "• **'categories'** — List all categories")

    # Low stock query
    if 'low stock' in message or 'out of stock' in message or 'restock' in message:
        products = Product.query.filter(Product.quantity < LOW_STOCK_THRESHOLD).order_by(Product.quantity).all()
        if products:
            items = '\n'.join([f"• **{p.name}**: {p.quantity} units left" for p in products[:5]])
            return f"⚠️ **Low Stock Alert** ({len(products)} items):\n{items}"
        return "✅ All products are well-stocked! No items below the threshold."

    # Total products
    if 'total product' in message or 'how many product' in message or 'product count' in message:
        count = Product.query.count()
        return f"📦 You currently have **{count} products** in your inventory."

    # Total sales
    if 'total sale' in message or 'revenue' in message or 'how much' in message:
        total = db.session.query(func.sum(Sale.revenue)).scalar() or 0
        count = Sale.query.count()
        return f"💰 **Total Revenue**: ${total:,.2f} from **{count} sales** recorded."

    # Search for a product
    if 'search' in message or 'find' in message or 'look up' in message:
        # Extract product name (remove keywords)
        terms = message.replace('search', '').replace('find', '').replace('look up', '').strip()
        if terms:
            products = Product.query.filter(Product.name.ilike(f'%{terms}%')).all()
            if products:
                items = '\n'.join([f"• **{p.name}** ({p.category}) — ${p.price:.2f} — Stock: {p.quantity}" for p in products[:5]])
                return f"🔍 Found {len(products)} product(s):\n{items}"
            return f"🔍 No products found matching '{terms}'."
        return "🔍 Please specify what you'd like to search for. Example: 'search laptop'"

    # Top products
    if 'top product' in message or 'best sell' in message or 'popular' in message:
        results = db.session.query(
            Product.name,
            func.sum(Sale.quantity_sold).label('total')
        ).join(Sale).group_by(Product.id).order_by(func.sum(Sale.quantity_sold).desc()).limit(5).all()

        if results:
            items = '\n'.join([f"• **{r.name}**: {int(r.total)} sold" for r in results])
            return f"🏆 **Top Selling Products**:\n{items}"
        return "📊 No sales data available yet."

    # Categories
    if 'categor' in message:
        categories = db.session.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
        if categories:
            items = '\n'.join([f"• **{c[0]}**: {c[1]} products" for c in categories])
            return f"📂 **Product Categories**:\n{items}"
        return "📂 No categories found."

    # Default fallback
    return ("🤔 I'm not sure about that. Try asking me:\n"
            "• 'Show low stock'\n"
            "• 'Total products'\n"
            "• 'Total sales'\n"
            "• 'Search [product name]'\n"
            "• 'Top products'\n"
            "• Type **'help'** for all commands")
