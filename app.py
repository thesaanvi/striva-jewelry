import os
import json
from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'striva_luxury_secret_key_2026_expanded')

# -------------------------------------------------------------------
# Database Configuration & Connection Management
# -------------------------------------------------------------------
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'striva_db')

def get_db_connection():
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

# Expanded Master Product Catalog
EXPANDED_PRODUCTS = [
    # --- WOMEN (MINIMAL & DAILY) - MAX ₹7,000 ---
    ("Aura Solitaire Ring", "women", "bestseller", 3499.00, "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "18k Gold Vermeil solitaire ring with brilliant diamond-cut stone."),
    ("Lumière Pearl Necklace", "women", "favorite", 2799.00, "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Freshwater cultured pearl suspended from a delicate gold chain."),
    ("Celestial Star Pendant", "women", "trendy", 3199.00, "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=600&q=80", "TRENDY", "Star medallion embedded with brilliant zircon accents."),
    ("Luna Crescent Studs", "women", "favorite", 1999.00, "https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Minimalist moon-phase studs crafted in 925 Sterling Silver."),
    ("Twisted Gold Stacking Ring", "women", "trendy", 2499.00, "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=600&q=80", "TRENDY", "Subtle textured rope band designed for everyday stacking."),
    ("Classic Tennis Bracelet", "women", "bestseller", 5899.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "Continuous line of prong-set crystals in silver vermeil."),
    ("Elysian Emerald Choker", "women", "favorite", 6499.00, "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Faceted lab emerald charm on a fine gold link necklace."),
    ("Petal Hoop Earrings", "women", "trendy", 2299.00, "https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80", "TRENDY", "Lightweight textured petal hoops in vermeil finish."),

    # --- MEN (MINIMAL & DAILY) - MAX ₹7,000 ---
    ("Signet Heavy Gold Ring", "men", "trendy", 4999.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "TRENDY", "Solid brushed 18k gold vermeil signet ring."),
    ("Sovereign Cuban Chain", "men", "bestseller", 6499.00, "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "5mm classic Cuban link chain in silver."),
    ("Minimalist Gold Cuff", "men", "trendy", 3899.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "TRENDY", "Sleek open-cuff wrist band in heavy vermeil gold."),
    ("Bold Onyx Signet", "men", "favorite", 5200.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Natural black onyx stone set in solid 925 sterling silver."),
    ("Bar Link Silver Pendant", "men", "bestseller", 3100.00, "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "Architectural geometric bar pendant on a curb chain."),
    ("Brushed Titanium Band", "men", "trendy", 2800.00, "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=600&q=80", "TRENDY", "Durable matte-brushed modern everyday ring."),
    ("Executive Silver Cufflinks", "men", "favorite", 3600.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Classic square shirt cufflinks in polished sterling silver."),
    ("Box Chain Layered Necklace", "men", "bestseller", 4200.00, "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "Dual-layered minimal box chain necklace."),

    # --- WEDDING COLLECTION (WOMEN) - MAX ₹10,000 ---
    ("Eternity Diamond Wedding Band", "wedding", "bestseller", 8999.00, "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=600&q=80", "WEDDING", "Full micro-pave band crafted in 925 Sterling Silver."),
    ("Solitaire Diamond Mangalsutra", "wedding", "favorite", 9499.00, "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Modern single-pendant black bead gold mangalsutra chain."),
    ("Kundan Crescent Maang Tikka", "wedding", "trendy", 6800.00, "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=600&q=80", "WEDDING", "Traditional Kundan & pearl forehead ornament for modern brides."),
    ("Royal Pearl Nath / Nose Ring", "wedding", "favorite", 4200.00, "https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Non-pierced traditional bridal nose ring with pearl strand."),
    ("Opulent Crown Stacking Band", "wedding", "trendy", 8499.00, "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80", "TRENDY", "Tiara-contoured wedding ring studded with zircon stones."),
    ("Infinity Minimal Mangalsutra", "wedding", "bestseller", 7999.00, "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "Contemporary infinity symbol pendant with sacred black beads."),
    ("Heritage Temple Motif Nath", "wedding", "trendy", 4999.00, "https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80", "TRENDY", "Gold vermeil bridal nath with drop pearl accents."),

    # --- WEDDING COLLECTION (MEN) - MAX ₹10,000 ---
    ("Royal Couple Solitaire Band Set", "wedding", "favorite", 9999.00, "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Matching handcrafted groom and bride wedding bands."),
    ("Royal Sherwani Brooch", "wedding", "bestseller", 6800.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "WEDDING", "Embossed royal crest brooch with gemstone drop for wedding attire."),
    ("Multi-Strand Groom Pearl Necklace", "wedding", "favorite", 8500.00, "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Layered pearl & emerald-bead groom necklace for royal sherwanis."),
    ("Baroque Pearl Wedding Cufflinks", "wedding", "trendy", 5400.00, "https://images.unsplash.com/photo-1611591475150-184589d7010f?auto=format&fit=crop&w=600&q=80", "TRENDY", "Gold vermeil ceremonial cufflinks featuring baroque pearls."),
    ("His & Hers Promise Band Set", "wedding", "bestseller", 7499.00, "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=600&q=80", "BESTSELLER", "Dual-band matrimonial commitment collection."),
    ("Emerald Sherwani Kalgi / Brooch", "wedding", "favorite", 8900.00, "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=600&q=80", "OUR FAVORITE", "Traditional wedding turban kalgi pin with emerald green drops."),
    ("Groom Regal Kundan Haar", "wedding", "trendy", 9800.00, "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=600&q=80", "TRENDY", "Grand ceremonial groom necklace handcrafted with Kundan work.")
]

def init_db_schema():
    conn = get_db_connection()
    if not conn:
        print("[DATABASE NOTICE] Running with memory catalog (Database disconnected).")
        return

    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                collection VARCHAR(50) DEFAULT 'trendy',
                price DECIMAL(10, 2) NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                tag VARCHAR(50) DEFAULT 'NEW',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

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

        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]

        if count < len(EXPANDED_PRODUCTS):
            cursor.execute("TRUNCATE TABLE products")
            insert_sql = """
                INSERT INTO products (name, category, collection, price, image_url, tag, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_sql, EXPANDED_PRODUCTS)
            conn.commit()

        cursor.close()
        conn.close()
    except Error as e:
        print(f"[DATABASE ERROR] Initialization failed: {e}")

init_db_schema()

# -------------------------------------------------------------------
# Web Routes & API
# -------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category', 'all').strip().lower()
    collection = request.args.get('collection', 'all').strip().lower()
    
    try:
        max_price = float(request.args.get('max_price', 10000.0))
    except (ValueError, TypeError):
        max_price = 10000.0

    conn = get_db_connection()
    products = []

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, name, category, collection, price, image_url, tag, description FROM products WHERE price <= %s"
            params = [max_price]

            if category != 'all':
                query += " AND LOWER(category) = %s"
                params.append(category)

            if collection != 'all':
                query += " AND LOWER(collection) = %s"
                params.append(collection)

            query += " ORDER BY id ASC"
            cursor.execute(query, params)
            products = cursor.fetchall()

            for p in products:
                p['price'] = float(p['price'])

            cursor.close()
            conn.close()
        except Error as err:
            print(f"[API ERROR] Database query failed: {err}")

    # Fallback to local array if DB unavailable
    if not products:
        fallback_list = []
        for idx, item in enumerate(EXPANDED_PRODUCTS, 1):
            fallback_list.append({
                "id": idx,
                "name": item[0],
                "category": item[1],
                "collection": item[2],
                "price": item[3],
                "image_url": item[4],
                "tag": item[5],
                "description": item[6]
            })

        products = [
            p for p in fallback_list
            if (category == 'all' or p['category'] == category)
            and (collection == 'all' or p['collection'] == collection)
            and p['price'] <= max_price
        ]

    return jsonify({"products": products, "count": len(products)})

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    user_name = session.get('user_name')
    return jsonify({"loggedIn": bool(user_name), "userName": user_name})

@app.route('/api/auth/signin', methods=['POST'])
def auth_signin():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"success": False, "message": "Client name required."}), 400
    session['user_name'] = name
    return jsonify({"success": True, "userName": name})

@app.route('/api/auth/signout', methods=['POST'])
def auth_signout():
    session.pop('user_name', None)
    return jsonify({"success": True})

@app.route('/api/orders/place', methods=['POST'])
def place_order():
    data = request.get_json() or {}
    cart_items = data.get('cart', [])
    user_name = session.get('user_name', 'Valued Client')

    if not cart_items:
        return jsonify({"success": False, "message": "Bag is empty."}), 400

    total_amount = sum(float(item.get('price', 0)) for item in cart_items)
    conn = get_db_connection()
    order_id = None

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (user_name, user_identifier, total_amount, items_json) VALUES (%s, %s, %s, %s)",
                (user_name, "client@striva.com", total_amount, json.dumps(cart_items))
            )
            conn.commit()
            order_id = cursor.lastrowid
            cursor.close()
            conn.close()
        except Error as err:
            print(f"[ORDER ERROR] {err}")

    return jsonify({
        "success": True,
        "orderId": order_id if order_id else "STRIVA-2026-CONFIRMED",
        "totalAmount": total_amount,
        "message": "Order successfully received!"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
