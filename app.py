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
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            gender VARCHAR(20) NOT NULL,
            occasion VARCHAR(20) NOT NULL,
            sub_category VARCHAR(50) NOT NULL,
            price_inr DECIMAL(10,2) NOT NULL,
            metal VARCHAR(100) NOT NULL,
            description TEXT,
            image_url TEXT,
            tag VARCHAR(50),
            is_customizable BOOLEAN DEFAULT TRUE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            items_json TEXT NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'Processing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)

        # Refresh catalog with premium demi-fine imagery
        cursor.execute("TRUNCATE TABLE products")
        
        demi_fine_catalog = [
            # WOMEN - MINIMAL (999 - 7000)
            ('Solitaire Vermeil Ring', 'women', 'minimal', 'rings', 2499.00, '18K Gold Vermeil', 'Solid 18K gold vermeil band featuring a brilliant diamond-cut bezel gemstone.', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop&q=80', 'bestseller', True),
            ('Celestial Huggie Hoop Earrings', 'women', 'minimal', 'earring', 1999.00, '18K Rose Gold Vermeil', 'Daily water-safe huggies inlaid with micro paved zirconia.', 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&auto=format&fit=crop&q=80', 'trending', True),
            ('Sleek Snake Chain Necklace', 'women', 'minimal', 'necklaces', 3899.00, '925 Sterling Silver', 'High-polish anti-tarnish liquid silver fluid chain.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80', 'favourites', True),
            ('Minimalist Stacking Cuff', 'women', 'minimal', 'bracelets', 2999.00, '18K Gold Vermeil', 'Open-ended sleek gold vermeil wrist cuff.', 'https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=800&auto=format&fit=crop&q=80', 'bestseller', True),
            ('Delicate Gold Bead Anklet', 'women', 'minimal', 'anklets', 1499.00, '18K Gold Vermeil', 'Waterproof everyday gold bead anklet with secure clasp.', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&auto=format&fit=crop&q=80', 'festive', True),

            # MEN - MINIMAL (999 - 7000)
            ('Homme Brushed Signet Ring', 'men', 'minimal', 'rings', 2899.00, '925 Sterling Silver', 'Hand-finished brushed silver geometric signet ring.', 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&auto=format&fit=crop&q=80', 'bestseller', True),
            ('Classic Beveled Curb Chain', 'men', 'minimal', 'chains', 4999.00, '925 Sterling Silver', '4mm solid sterling silver link chain for everyday wear.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80', 'trending', False),
            ('Textured Gold Kada Cuff', 'men', 'minimal', 'bracelets', 4200.00, '18K Gold Vermeil', 'Hammered architectural gold cuff designed for modern men.', 'https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=800&auto=format&fit=crop&q=80', 'favourites', True),
            ('Single Huggie Ear Piercing', 'men', 'minimal', 'piercings', 1199.00, '925 Sterling Silver', 'Hypoallergenic lightweight daily hoop earring.', 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&auto=format&fit=crop&q=80', 'festive', False),

            # WOMEN - WEDDING (UP TO 9000)
            ('Royal Heritage Nath (Nose Ring)', 'women', 'wedding', 'noserings', 3499.00, '18K Gold Vermeil & Pearl', 'Lightweight bridal nose ring strung with natural pearls.', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&auto=format&fit=crop&q=80', 'festive', False),
            ('Kundan Crescent Maang Tika', 'women', 'wedding', 'mang tika', 3199.00, 'Gold Vermeil & Kundan', 'Handcrafted lightweight maang tika for wedding functions.', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&auto=format&fit=crop&q=80', 'trending', False),
            ('Modern Solitaire Mangalsutra', 'women', 'wedding', 'mangalsutra', 6899.00, '18K Gold Vermeil', 'Minimal dual-bead gold chain with solitaire diamond pendant.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80', 'bestseller', True),
            ('Bridal Vermeil Choker', 'women', 'wedding', 'necklaces', 8999.00, '18K Gold Vermeil', 'Intricate lightweight festive choker set.', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&auto=format&fit=crop&q=80', 'favourites', False),

            # MEN - WEDDING (UP TO 9000)
            ('Royal Emerald Coat Brooch', 'men', 'wedding', 'brooch', 4200.00, 'Brass Gold & Emerald CZ', 'Regal sherwani coat pin crafted with micro-pave stones.', 'https://images.unsplash.com/photo-1600003014755-ba31aa59c4b6?w=800&auto=format&fit=crop&q=80', 'festive', False),
            ('Groom Pearl Layered Necklace', 'men', 'wedding', 'necklace', 7999.00, 'Cultured Pearls & Vermeil', 'Traditional multi-strand royal groomsmen layered necklace.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80', 'trending', False)
        ]
        
        cursor.executemany("""
            INSERT INTO products (name, gender, occasion, sub_category, price_inr, metal, description, image_url, tag, is_customizable) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, demi_fine_catalog)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"DB Init Exception: {e}")

init_db()

@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        hashed_pwd = generate_password_hash(data['password'])
        cursor.execute("INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)", 
                       (data['name'], data['email'], hashed_pwd))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'user': {'id': user_id, 'name': data['name'], 'email': data['email']}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Email address already registered'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password_hash'], data['password']):
            return jsonify({'status': 'success', 'user': {'id': user['id'], 'name': user['full_name'], 'email': user['email']}})
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    gender = request.args.get('gender')
    occasion = request.args.get('occasion')
    sub_category = request.args.get('sub_category')
    tag = request.args.get('tag')
    max_price = request.args.get('max_price')

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if gender and gender != 'all':
            query += " AND gender = %s"
            params.append(gender)
        if occasion and occasion != 'all':
            query += " AND occasion = %s"
            params.append(occasion)
        if sub_category and sub_category != 'all':
            query += " AND sub_category = %s"
            params.append(sub_category)
        if tag and tag != 'all':
            query += " AND tag = %s"
            params.append(tag)
        if max_price:
            query += " AND price_inr <= %s"
            params.append(max_price)

        cursor.execute(query, params)
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (user_id, items_json, total_amount) VALUES (%s, %s, %s)",
                       (data['user_id'], str(data['items']), data['total_amount']))
        conn.commit()
        order_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'order_id': order_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'orders': orders})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
