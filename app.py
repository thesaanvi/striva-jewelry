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
        
        # Table: Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Table: Products
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

        # Table: Orders
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

        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            demo_products = [
                # Minimal Women (999 - 7000)
                ('Solitaire Vermeil Ring', 'women', 'minimal', 'rings', 1499.00, '18K Gold Vermeil', 'Elegant 18K Gold Vermeil single stone solitaire band.', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600', 'bestseller', True),
                ('Celestial Hoop Earrings', 'women', 'minimal', 'earring', 2299.00, '18K Gold Vermeil', 'Lightweight daily hoops with delicate cubic zirconia accents.', 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=600', 'trending', True),
                ('Twisted Snake Chain Necklace', 'women', 'minimal', 'necklaces', 3499.00, '925 Sterling Silver', 'Liquid gold finish anti-tarnish everyday chain.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600', 'favourites', True),
                ('Delicate Beaded Anklet', 'women', 'minimal', 'anklets', 1299.00, '18K Gold Vermeil', 'Waterproof everyday gold bead anklet.', 'https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=600', 'festive', True),
                ('Minimalist Cuff Bracelet', 'women', 'minimal', 'bracelets', 2799.00, '18K Gold Vermeil', 'Sleek open cuff designed for stacking.', 'https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=600', 'bestseller', True),

                # Minimal Men (999 - 7000)
                ('Homme Signet Ring', 'men', 'minimal', 'rings', 2499.00, '925 Sterling Silver', 'Brushed silver classic crest signet ring.', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600', 'bestseller', True),
                ('Heavy Curb Chain', 'men', 'minimal', 'chains', 4999.00, '925 Sterling Silver', 'Solid sterling silver 4mm bevelled curb chain.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600', 'trending', False),
                ('Textured Gold Cuff Bracelet', 'men', 'minimal', 'bracelets', 3899.00, '18K Gold Vermeil', 'Hand-hammered gold vermeil structured cuff.', 'https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=600', 'favourites', True),
                ('Single Huggie Piercing Stud', 'men', 'minimal', 'piercings', 999.00, '925 Sterling Silver', 'Hypoallergenic daily hoop stud for men.', 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=600', 'festive', False),

                # Wedding Women (Up to 9000)
                ('Royal Kundan Nose Ring (Nath)', 'women', 'wedding', 'noserings', 3499.00, 'Gold Foil & Kundan', 'Lightweight regal nath set with freshwater pearls.', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600', 'festive', False),
                ('Grand Pearl Maang Tika', 'women', 'wedding', 'mang tika', 2899.00, '18K Gold Vermeil', 'Anti-tarnish statement bridal headpiece.', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600', 'trending', False),
                ('Solitaire Diamond Mangalsutra', 'women', 'wedding', 'mangalsutra', 6899.00, '18K Gold Vermeil', 'Modern lightweight daily wear mangalsutra chain.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600', 'bestseller', True),
                ('Bridal Choker Necklace', 'women', 'wedding', 'necklaces', 8999.00, 'Gold Vermeil & Kundan', 'Lightweight festive choker designed for comfort.', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600', 'favourites', False),

                # Wedding Men (Up to 9000)
                ('Royal Emerald Sherwani Brooch', 'men', 'wedding', 'brooch', 4500.00, 'Brass Gold & Cubic Zirconia', 'Traditional royal coat pin with micro-pave stones.', 'https://images.unsplash.com/photo-1600003014755-ba31aa59c4b6?w=600', 'festive', False),
                ('Groom Layered Pearl Necklace', 'men', 'wedding', 'necklace', 7999.00, 'Natural Cultured Pearls', 'Multi-strand groomsmen layered statement necklace.', 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600', 'trending', False)
            ]
            cursor.executemany("""
                INSERT INTO products (name, gender, occasion, sub_category, price_inr, metal, description, image_url, tag, is_customizable) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, demo_products)

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
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 400

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
