import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
from mysql.connector import Error, pooling

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'striva_secret_key_2026_dev')

# ---------------------------------------------------------
# DATABASE CONFIGURATION (Aiven MySQL / Local MySQL)
# ---------------------------------------------------------
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'striva_db')

def get_db_connection():
    """Establish and return a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl_ca=os.environ.get('SSL_CA_PATH', None) if os.environ.get('DB_HOST') else None
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# ---------------------------------------------------------
# PAGE RENDERING ROUTES
# ---------------------------------------------------------

@app.route('/')
def index():
    """Home Page Route"""
    conn = get_db_connection()
    featured_products = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE is_featured = 1 LIMIT 6")
            featured_products = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Database query error: {e}")
            if conn.is_connected():
                conn.close()
    return render_template('index.html', products=featured_products)

@app.route('/catalog')
def catalog():
    """Product Catalog Route with Category Filtering"""
    category = request.args.get('category', 'all')
    conn = get_db_connection()
    products = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            if category != 'all':
                cursor.execute("SELECT * FROM products WHERE category = %s", (category,))
            else:
                cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Database query error: {e}")
            if conn.is_connected():
                conn.close()
    return render_template('catalog.html', products=products, selected_category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Single Product Details Page Route"""
    conn = get_db_connection()
    product = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Database query error: {e}")
            if conn.is_connected():
                conn.close()
    
    if not product:
        return render_template('404.html'), 404

    return render_template('product_detail.html', product=product)

@app.route('/cart')
def view_cart():
    """Cart View Route"""
    cart = session.get('cart', {})
    conn = get_db_connection()
    cart_items = []
    total_price = 0.0

    if conn and cart:
        try:
            cursor = conn.cursor(dictionary=True)
            format_strings = ','.join(['%s'] * len(cart))
            cursor.execute(f"SELECT * FROM products WHERE id IN ({format_strings})", list(cart.keys()))
            items = cursor.fetchall()
            
            for item in items:
                p_id = str(item['id'])
                qty = cart[p_id]
                subtotal = float(item['price']) * qty
                total_price += subtotal
                cart_items.append({
                    'id': item['id'],
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': qty,
                    'subtotal': subtotal,
                    'image': item.get('image_url', '')
                })
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error fetching cart details: {e}")
            if conn.is_connected():
                conn.close()

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/contact')
def contact():
    """Contact & Inquiries Page Route"""
    return render_template('contact.html')

# ---------------------------------------------------------
# API & ACTION ENDPOINTS (CART & FORM SUBMISSIONS)
# ---------------------------------------------------------

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add Item to Session Cart"""
    data = request.get_json() if request.is_json else request.form
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))

    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400

    cart = session.get('cart', {})
    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    session['cart'] = cart
    session.modified = True

    total_count = sum(cart.values())
    return jsonify({
        'success': True,
        'message': 'Product added to cart successfully!',
        'cart_count': total_count
    })

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove Item from Session Cart"""
    data = request.get_json() if request.is_json else request.form
    product_id = str(data.get('product_id'))

    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        session.modified = True

    total_count = sum(cart.values())
    return jsonify({
        'success': True,
        'message': 'Product removed from cart',
        'cart_count': total_count
    })

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    """Clear All Items from Cart"""
    session['cart'] = {}
    session.modified = True
    return jsonify({'success': True, 'message': 'Cart cleared successfully'})

@app.route('/api/contact/submit', methods=['POST'])
def submit_contact_form():
    """Save Contact Form Submission to MySQL"""
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO inquiries (name, email, message) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, message))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Thank you! Your message has been received.'})
        except Error as e:
            print(f"Error saving inquiry: {e}")
            if conn.is_connected():
                conn.close()
            return jsonify({'success': False, 'message': 'Database error. Please try again later.'}), 500

    return jsonify({'success': False, 'message': 'Database connection failed.'}), 500

# ---------------------------------------------------------
# DATABASE INITIALIZATION SCRIPT (FOR PRACTICAL MANUAL)
# ---------------------------------------------------------

@app.route('/admin/init-db', methods=['GET'])
def init_db():
    """Utility route to initialize database tables if they do not exist."""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'Failed', 'message': 'Could not connect to database'}), 500

    try:
        cursor = conn.cursor()
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                description TEXT,
                image_url VARCHAR(500),
                is_featured TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Inquiries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inquiries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'Success', 'message': 'Database tables created successfully!'})
    except Error as e:
        if conn.is_connected():
            conn.close()
        return jsonify({'status': 'Error', 'message': str(e)}), 500

# ---------------------------------------------------------
# ERROR HANDLERS & SERVER LAUNCH
# ---------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Debug mode should be set to False in production deployment (Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
