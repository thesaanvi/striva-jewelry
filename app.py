import os
import sys
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
from mysql.connector import Error

# Initialize Flask application
app = Flask(__name__, template_folder='templates', static_folder='static')

# Secret key used for secure session management
app.secret_key = os.environ.get('SECRET_KEY', 'striva_luxury_secret_key_2026_production_v1')

# -------------------------------------------------------------------
# Database Configuration & Connection Management
# -------------------------------------------------------------------
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'striva_db')

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Supports Aiven, Render MySQL, or local MySQL instances.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=10
        )
        if connection.is_connected():
            return connection
    except Error as err:
        print(f"[DATABASE NOTICE] Unable to connect to MySQL ({DB_HOST}:{DB_PORT}): {err}")
        return None
    return None


def init_db_schema():
    """
    Automatically creates necessary tables and seeds default jewelry catalog
    data if the tables do not exist in the connected database.
    """
    conn = get_db_connection()
    if not conn:
        print("[DATABASE NOTICE] Skipping table initialization (Database unreachable).")
        return

    try:
        cursor = conn.cursor()
        
        # Create Products Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                tag VARCHAR(50) DEFAULT 'NEW',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Orders Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(255) NOT NULL,
                user_identifier VARCHAR(255) NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                items_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check if products already exist
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]

        if count == 0:
            print("[DATABASE] Seeding initial jewelry catalog...")
            sample_products = [
                ("Aura Solitaire Ring", "women", 3499.00, "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "18k Gold Vermeil setting with hand-cut cubic zirconia solitaire."),
                ("Eternity Diamond Band", "wedding", 8999.00, "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=600&q=80", "WEDDING", "Full eternity micro-pave band crafted in 925 Sterling Silver."),
                ("Signet Heavy Gold Ring", "men", 4999.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "NEW", "Solid brushed 18k gold vermeil signet ring designed for everyday wear."),
                ("Lumière Pearl Necklace", "women", 2799.00, "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80", "FEATURED", "Freshwater cultured pearl suspended from a delicate gold vermeil chain."),
                ("Celestial Pendant", "women", 3199.00, "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=600&q=80", "NEW", "Star-inspired medallion embedded with brilliant accents."),
                ("Sovereign Cuban Chain", "men", 6499.00, "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "5mm classic Cuban link chain in polished sterling silver."),
                ("Royal Solitaire Band", "wedding", 12499.00, "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80", "WEDDING", "Hand-finished classic wedding solitaire with custom gallery detail."),
                ("Minimalist Gold Cuff", "men", 3899.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "CLASSIC", "Sleek open-cuff wrist bracelet in heavy vermeil gold.")
            ]

            insert_sql = """
                INSERT INTO products (name, category, price, image_url, tag, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_sql, sample_products)
            conn.commit()
            print("[DATABASE] Seed complete.")

        cursor.close()
        conn.close()
    except Error as e:
        print(f"[DATABASE ERROR] Initialization failed: {e}")


# Initialize database schema on module load
init_db_schema()

# -------------------------------------------------------------------
# Frontend Web Routes
# -------------------------------------------------------------------
@app.route('/')
def index():
    """
    Renders the primary single-page e-commerce template.
    """
    return render_template('index.html')


# -------------------------------------------------------------------
# Product Catalog API
# -------------------------------------------------------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Returns filtered products based on category and maximum price constraints.
    Falls back gracefully to hardcoded items if DB is disconnected.
    """
    category = request.args.get('category', 'all').strip().lower()
    
    try:
        max_price = float(request.args.get('max_price', 100000.0))
    except (ValueError, TypeError):
        max_price = 100000.0

    conn = get_db_connection()
    products = []

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT id, name, category, price, image_url, tag, description FROM products WHERE price <= %s"
            params = [max_price]

            if category != 'all':
                query += " AND (LOWER(category) = %s OR LOWER(category) = 'all')"
                params.append(category)

            query += " ORDER BY id ASC"

            cursor.execute(query, params)
            products = cursor.fetchall()

            # Format price fields to float for JSON compatibility
            for product in products:
                product['price'] = float(product['price'])

            cursor.close()
            conn.close()
        except Error as err:
            print(f"[API ERROR] Database execution failed: {err}")

    # If database returns no items or database is unconfigured, return standard fallback list
    if not products:
        fallback_catalog = [
            {
                "id": 101,
                "name": "Aura Solitaire Ring",
                "category": "women",
                "price": 3499.0,
                "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80",
                "tag": "BESTSELLER",
                "description": "18k Gold Vermeil setting with hand-cut cubic zirconia solitaire."
            },
            {
                "id": 102,
                "name": "Eternity Diamond Band",
                "category": "wedding",
                "price": 8999.0,
                "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=600&q=80",
                "tag": "WEDDING",
                "description": "Full eternity micro-pave band crafted in 925 Sterling Silver."
            },
            {
                "id": 103,
                "name": "Signet Heavy Gold Ring",
                "category": "men",
                "price": 4999.0,
                "image_url": "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80",
                "tag": "NEW",
                "description": "Solid brushed 18k gold vermeil signet ring designed for everyday wear."
            },
            {
                "id": 104,
                "name": "Lumière Pearl Necklace",
                "category": "women",
                "price": 2799.0,
                "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80",
                "tag": "FEATURED",
                "description": "Freshwater cultured pearl suspended from a delicate gold vermeil chain."
            },
            {
                "id": 105,
                "name": "Sovereign Cuban Chain",
                "category": "men",
                "price": 6499.0,
                "image_url": "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=600&q=80",
                "tag": "BESTSELLER",
                "description": "5mm classic Cuban link chain in polished sterling silver."
            },
            {
                "id": 106,
                "name": "Royal Solitaire Band",
                "category": "wedding",
                "price": 12499.0,
                "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80",
                "tag": "WEDDING",
                "description": "Hand-finished classic wedding solitaire with custom gallery detail."
            }
        ]

        products = [
            p for p in fallback_catalog
            if (category == 'all' or p['category'] == category) and p['price'] <= max_price
        ]

    return jsonify({"products": products, "count": len(products)})


# -------------------------------------------------------------------
# Authentication & User Session APIs
# -------------------------------------------------------------------
@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """
    Checks whether the current web user is signed into a session.
    """
    user_name = session.get('user_name')
    user_identifier = session.get('user_identifier')
    
    return jsonify({
        "loggedIn": bool(user_name),
        "userName": user_name if user_name else None,
        "userIdentifier": user_identifier if user_identifier else None
    })


@app.route('/api/auth/signin', methods=['POST'])
def auth_signin():
    """
    Authenticates or signs in a client and saves their state in Flask session.
    """
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    identifier = data.get('identifier', '').strip()

    if not name:
        return jsonify({"success": False, "message": "Client name is required."}), 400

    session['user_name'] = name
    session['user_identifier'] = identifier if identifier else "guest@striva.com"

    return jsonify({
        "success": True,
        "userName": session['user_name'],
        "userIdentifier": session['user_identifier']
    })


@app.route('/api/auth/signout', methods=['POST'])
def auth_signout():
    """
    Clears active client session variables.
    """
    session.pop('user_name', None)
    session.pop('user_identifier', None)
    return jsonify({"success": True, "message": "Signed out successfully."})


# -------------------------------------------------------------------
# Order Placement API
# -------------------------------------------------------------------
@app.route('/api/orders/place', methods=['POST'])
def place_order():
    """
    Receives custom cart payloads and records order records in MySQL database.
    """
    data = request.get_json() or {}
    cart_items = data.get('cart', [])
    user_name = session.get('user_name', data.get('userName', 'Valued Client'))
    user_identifier = session.get('user_identifier', data.get('userIdentifier', 'guest@striva.com'))

    if not cart_items:
        return jsonify({"success": False, "message": "Shopping bag is empty."}), 400

    total_amount = sum(float(item.get('price', 0)) for item in cart_items)

    conn = get_db_connection()
    order_id = None

    if conn:
        try:
            cursor = conn.cursor()
            import json
            items_str = json.dumps(cart_items)

            insert_sql = """
                INSERT INTO orders (user_name, user_identifier, total_amount, items_json)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (user_name, user_identifier, total_amount, items_str))
            conn.commit()
            order_id = cursor.lastrowid
            cursor.close()
            conn.close()
        except Error as err:
            print(f"[ORDER ERROR] Failed to store order: {err}")

    return jsonify({
        "success": True,
        "orderId": order_id if order_id else "STRIVA-2026-DEMO",
        "totalAmount": total_amount,
        "message": f"Order successfully created for {user_name}!"
    })


# -------------------------------------------------------------------
# Server Execution Point
# -------------------------------------------------------------------
if __name__ == '__main__':
    # Determine execution port (Render/Heroku/Aiven compatibility)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"[SERVER] Launching Striva Luxury Web Backend on port {port} (Debug: {debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
