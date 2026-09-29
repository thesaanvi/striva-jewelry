import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
CORS(app)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
    )

def init_db():
    """Automatically builds tables and inserts default products on startup"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            phone_number VARCHAR(20) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price_inr DECIMAL(10,2) NOT NULL,
            metal VARCHAR(100) NOT NULL,
            image_url TEXT,
            is_customizable BOOLEAN DEFAULT FALSE
        );
        """)

        # Check if products already exist
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]

        if count == 0:
            products = [
                ('Classic Solitaire Vermeil Ring', 'women', 3499.00, '18K Gold Vermeil', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500', True),
                ('Layered Celestial Pendant', 'women', 5999.00, '18K Gold Vermeil', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500', True),
                ('Heritage Kundan Choker', 'wedding', 18500.00, 'Lightweight Brass Gold', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500', False),
                ('Lightweight Rani Haar Necklace', 'wedding', 32000.00, 'Gold Foil & Kundan', 'https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=500', False),
                ('Royal Bridal Haathphool Set', 'wedding', 12400.00, 'Anti-Tarnish Vermeil', 'https://images.unsplash.com/photo-1600003014755-ba31aa59c4b6?w=500', False),
                ('Men Solid Curb Chain', 'men', 8999.00, '925 Sterling Silver', 'https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=500', True),
                ('Homme Textured Gold Kada', 'men', 14500.00, '18K Gold Vermeil', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500', True)
            ]
            cursor.executemany("""
                INSERT INTO products (name, category, price_inr, metal, image_url, is_customizable) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, products)

        conn.commit()
        cursor.close()
        conn.close()
        print("Database setup completed automatically!")
    except Exception as e:
        print(f"Database initialization note: {e}")

# Run automatic setup when backend starts
init_db()

@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    max_price = request.args.get('max_price', 50000)
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM products WHERE price_inr <= %s"
        params = [max_price]
        
        if category and category != 'all':
            query += " AND category = %s"
            params.append(category)
            
        cursor.execute(query, params)
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier')
    password = data.get('password')

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s OR phone_number = %s", (identifier, identifier))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            return jsonify({'status': 'success', 'user': {'id': user['id'], 'name': user['full_name']}})
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
