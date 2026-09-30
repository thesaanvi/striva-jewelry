import os
import pymysql
import pymysql.cursors
from flask import Flask, jsonify, request, render_template_string

# Safe import for dotenv so it never crashes if missing locally or in production
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# Environment variables setup
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = int(os.environ.get('DB_PORT', 3306)) if os.environ.get('DB_PORT') else 3306

# Fallback catalog data used if the live MySQL database is unreachable
FALLBACK_PRODUCTS = [
    {
        "id": 1,
        "name": "Aura Solitaire Diamond Ring",
        "gender": "female",
        "occasion": "minimal",
        "category": "rings",
        "price": 1499,
        "section": "trending",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80"
    },
    {
        "id": 2,
        "name": "Elegance Pearl Layered Necklace",
        "gender": "female",
        "occasion": "minimal",
        "category": "necklace chain",
        "price": 2499,
        "section": "best_sellers",
        "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&q=80"
    },
    {
        "id": 3,
        "name": "Crystal Charm Silver Anklet",
        "gender": "female",
        "occasion": "minimal",
        "category": "anklets",
        "price": 1299,
        "section": "curators_choice",
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80"
    },
    {
        "id": 4,
        "name": "Royal Emerald Maang Tikka",
        "gender": "female",
        "occasion": "wedding",
        "category": "mang tikka",
        "price": 4999,
        "section": "curators_choice",
        "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80"
    },
    {
        "id": 5,
        "name": "Kundan Floral Nose Ring",
        "gender": "female",
        "occasion": "wedding",
        "category": "nosering",
        "price": 1999,
        "section": "trending",
        "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80"
    },
    {
        "id": 6,
        "name": "18k Gold Vermeil Mangalsutra",
        "gender": "female",
        "occasion": "wedding",
        "category": "mangalsutra",
        "price": 5999,
        "section": "best_sellers",
        "image": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=500&q=80"
    },
    {
        "id": 7,
        "name": "Sleek Titanium Men's Band",
        "gender": "male",
        "occasion": "minimal",
        "category": "rings",
        "price": 1899,
        "section": "trending",
        "image": "https://images.unsplash.com/photo-1603561596112-0a132b757442?w=500&q=80"
    },
    {
        "id": 8,
        "name": "Classic Heavy Men's Gold Chain",
        "gender": "male",
        "occasion": "wedding",
        "category": "necklace chain",
        "price": 6999,
        "section": "best_sellers",
        "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80"
    },
    {
        "id": 9,
        "name": "Cuban Link Men's Bracelet",
        "gender": "male",
        "occasion": "minimal",
        "category": "bracelets",
        "price": 2299,
        "section": "curators_choice",
        "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80"
    },
    {
        "id": 10,
        "name": "Forever Love Matching Couple Bands",
        "gender": "couple",
        "occasion": "wedding",
        "category": "rings",
        "price": 4499,
        "section": "trending",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80"
    },
    {
        "id": 11,
        "name": "Dual Promise Key-Lock Pendants",
        "gender": "couple",
        "occasion": "minimal",
        "category": "necklace chain",
        "price": 3199,
        "section": "best_sellers",
        "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&q=80"
    }
]

def get_db_connection():
    if not DB_HOST or not DB_USER:
        return None
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        ssl={'ssl': {}},
        connect_timeout=5
    )

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "Error: index.html file not found in current directory.", 404

@app.route('/api/products', methods=['GET'])
def get_products():
    gender = request.args.get('gender', 'all')
    occasion = request.args.get('occasion', 'all')
    category = request.args.get('category', 'all')
    section = request.args.get('section', 'all')

    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                query = "SELECT * FROM products WHERE 1=1"
                params = []

                if gender != 'all':
                    query += " AND gender = %s"
                    params.append(gender)
                if occasion != 'all':
                    query += " AND occasion = %s"
                    params.append(occasion)
                if category != 'all':
                    query += " AND category = %s"
                    params.append(category)
                if section != 'all':
                    query += " AND section = %s"
                    params.append(section)

                cursor.execute(query, params)
                products = cursor.fetchall()
                conn.close()
                return jsonify(products)
    except Exception as e:
        app.logger.warning(f"Database query failed, serving fallback data. Error: {e}")
        if conn:
            try:
                conn.close()
            except:
                pass

    filtered = FALLBACK_PRODUCTS
    if gender != 'all':
        filtered = [p for p in filtered if p['gender'] == gender]
    if occasion != 'all':
        filtered = [p for p in filtered if p['occasion'] == occasion]
    if category != 'all':
        filtered = [p for p in filtered if p['category'] == category]
    if section != 'all':
        filtered = [p for p in filtered if p['section'] == section]

    return jsonify(filtered)

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"status": "error", "message": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
