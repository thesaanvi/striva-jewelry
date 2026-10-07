# -*- coding: utf-8 -*-
import os
import pymysql
import pymysql.cursors
from flask import Flask, jsonify, request, render_template_string

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = int(os.environ.get('DB_PORT', 3306)) if os.environ.get('DB_PORT') else 3306

# Seed Products matching the EXACT Frontend Schema
FALLBACK_PRODUCTS = [
    # --- WOMEN COLLECTION ---
    {
        "id": 1,
        "name": "Aurelia 18k Solitaire Ring",
        "collection": "women",
        "category": "ring",
        "price": 5400,
        "rating": 4.9,
        "reviews": 42,
        "image": "https://www.ornatejewels.com/cdn/shop/files/RJR05041YG_3.jpg?v=1758004949&width=900",
        "desc": "Handcrafted in 18k yellow gold vermeil over recycled sterling silver with a brilliant 1ct lab-grown solitaire diamond."
    },
    {
        "id": 2,
        "name": "Celeste Layered Serpent Necklace",
        "collection": "women",
        "category": "necklace",
        "price": 8950,
        "rating": 4.8,
        "reviews": 31,
        "image": "https://moncheri.in/cdn/shop/files/close-up-snake-pendant-green-eyes-cz-stones.webp?v=1774100893&width=1000",
        "desc": "A luxurious dual-strand chain necklace featuring a delicate snake chain paired with an emerald-accented pendant."
    },
    {
        "id": 3,
        "name": "Elysia Huggie Hoop Earrings",
        "collection": "women",
        "category": "earring",
        "price": 4800,
        "rating": 4.7,
        "reviews": 28,
        "image": "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRCvm0Eio6Swgceq6I94FAWZ7TmjlxWS1zu1M0FIWAONklZwqEbmkaglvPCKGDidrIigwlK0y3bqx48eGEIW4avy2hvEuHRnA",
        "desc": "Dainty pavé-set huggie hoops designed for 24/7 wear with secure click closures."
    },
    {
        "id": 4,
        "name": "Seraphina Tennis Bracelet",
        "collection": "women",
        "category": "bracelet",
        "price": 9950,
        "rating": 5.0,
        "reviews": 56,
        "image": "https://lorvelleco.com/cdn/shop/files/50.webp?v=1780434643&width=960",
        "desc": "An exquisite tennis bracelet encrusted with brilliant hand-set cubic zirconia stones."
    },
    {
        "id": 5,
        "name": "Lyra Geometric Statement Ring",
        "collection": "women",
        "category": "ring",
        "price": 6200,
        "rating": 4.6,
        "reviews": 19,
        "image": "https://kymee.in/cdn/shop/files/KRW0039_1.jpg?v=1752053564&width=493",
        "desc": "Architectural lines meet warm 18k gold vermeil for an everyday statement."
    },
    {
        "id": 6,
        "name": "Ophelia Pearl Drop Pendant",
        "collection": "women",
        "category": "necklace",
        "price": 5900,
        "rating": 4.9,
        "reviews": 38,
        "image": "https://pheeora.com.au/cdn/shop/files/baroque_pearl_silver_gold_necklace_1.jpg?v=1732170479&width=493",
        "desc": "A lustrous freshwater baroque pearl suspended from a delicate gold vermeil chain."
    },
    {
        "id": 7,
        "name": "Vesta Drop Chandelier Earrings",
        "collection": "women",
        "category": "earring",
        "price": 7500,
        "rating": 4.8,
        "reviews": 22,
        "image": "https://cdn2.zohoecommerce.com/product-images/buy-vanamala-green-stone-earrings-online.png/3274882000000447418/600x600?storefront_domain=www.svetara.com&format=webp",
        "desc": "Graceful cascading gemstone drops designed for evening galas and celebrations."
    },
    {
        "id": 8,
        "name": "Kiran Chunky Curb Bracelet",
        "collection": "women",
        "category": "bracelet",
        "price": 8200,
        "rating": 4.7,
        "reviews": 15,
        "image": "https://www.warrenjames.co.uk/_assets/images/products/images_grey/1000/VEBR011.jpg?v=2.6.0",
        "desc": "Bold yet lightweight curb link bracelet crafted in recycled 925 silver with heavy gold plating."
    },
    {
        "id": 9,
        "name": "Thalia Stacking Band Trio",
        "collection": "women",
        "category": "ring",
        "price": 6900,
        "rating": 4.9,
        "reviews": 44,
        "image": "https://i.etsystatic.com/5335581/r/il/e49390/1107944157/il_1588xN.1107944157_niiz.jpg",
        "desc": "A set of three interlockable rings in yellow, rose, and white gold finishes."
    },
    {
        "id": 10,
        "name": "Helena Coin Medallion Necklace",
        "collection": "women",
        "category": "necklace",
        "price": 7800,
        "rating": 4.8,
        "reviews": 33,
        "image": "https://templeofthesun.com.au/cdn/shop/files/temple-of-the-sun-palas-coin-necklace-gold-vermeil-1146881791.jpg?v=1755577931&width=1280",
        "desc": "Inspired by ancient Hellenistic coins, embossed with intricate goddess motifs."
    },
    {
        "id": 11,
        "name": "Astra Starburst Studs",
        "collection": "women",
        "category": "earring",
        "price": 3500,
        "rating": 4.9,
        "reviews": 50,
        "image": "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcTjKVPFejUD0-q_AfZve32afVjMIxTg6uZjXCUSzGIVVaLhkEEc9aFL_J1WjbcjJ9iDXY_7N01d05xl_DYdSj9Epg3Sv4-TRFfERxDWhhWnfI9lEc5T789OjQ",
        "desc": "Celestial starburst studs featuring a central zirconia sparkle."
    },
    {
        "id": 12,
        "name": "Iris Cuff Bangle",
        "collection": "women",
        "category": "bracelet",
        "price": 8800,
        "rating": 4.7,
        "reviews": 18,
        "image": "https://lajoyeria.co/cdn/shop/files/B3624_1.jpg?v=1758809644&width=990",
        "desc": "An open adjustable cuff bangle with polished gemstone ends."
    },
    {
        "id": 13,
        "name": "Nesta Emerald Cocktail Ring",
        "collection": "women",
        "category": "ring",
        "price": 4800,
        "rating": 4.9,
        "reviews": 29,
        "image": "https://shayn.in/cdn/shop/files/QA123001_1.webp?v=1757935668&width=1946",
        "desc": "A stunning emerald-cut green spinel centerpiece framed in halo crystals."
    },
    {
        "id": 14,
        "name": "Selene Crescent Moon Choker",
        "collection": "women",
        "category": "necklace",
        "price": 7200,
        "rating": 4.8,
        "reviews": 24,
        "image": "https://kymee.in/cdn/shop/files/KNP0009.3263copy.webp?v=1755837133&width=493",
        "desc": "A delicate crescent moon pendant adorned with micro pavé stones."
    },
    {
        "id": 15,
        "name": "Daphne Evil Eye Protection Bracelet",
        "collection": "women",
        "category": "bracelet",
        "price": 5200,
        "rating": 4.9,
        "reviews": 61,
        "image": "https://kymee.in/cdn/shop/files/KBC0052.511copy.webp?v=1755169150&width=493",
        "desc": "Enamel evil eye talisman set in 18k gold vermeil chain."
    },

    # --- MEN COLLECTION ---
    {
        "id": 16,
        "name": "Titanium & Gold Minimalist Band",
        "collection": "men",
        "category": "ring",
        "price": 6500,
        "rating": 4.8,
        "reviews": 35,
        "image": "https://newmanbands.com/wp-content/uploads/2021/03/masterly-titanium-ring-for-men-gold-finish-wedding-band-engagement-ring-for-guys.webp",
        "desc": "Robust brushed titanium core encased in a sleek 18k yellow gold vermeil stripe."
    },
    {
        "id": 17,
        "name": "Onyx Signet Ring for Men",
        "collection": "men",
        "category": "ring",
        "price": 8950,
        "rating": 4.9,
        "reviews": 40,
        "image": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQrKTJaL-qwlzYHbvqZJhfxFizfLQY7LdiLrFnaPr71YRLnhh16ruxtapEYVOLeERgZsnsv692qk6QyBLHagN9USb6cM5RCDQ",
        "desc": "Classic square signet ring featuring a polished black onyx stone inlay."
    },
    {
        "id": 18,
        "name": "Sleek Curb Chain Necklace (Men)",
        "collection": "men",
        "category": "necklace",
        "price": 9800,
        "rating": 4.9,
        "reviews": 52,
        "image": "https://i.etsystatic.com/13878029/r/il/da299e/3290617275/il_1588xN.3290617275_dft4.jpg",
        "desc": "Heavy 5mm curb chain crafted in recycled 925 silver with durable gold plating."
    },
    {
        "id": 19,
        "name": "Regal Gold Cufflinks",
        "collection": "men",
        "category": "traditional",
        "price": 3200,
        "rating": 4.7,
        "reviews": 21,
        "image": "https://tossido.in/cdn/shop/files/uptown-cufflinks-5149722_1000x.jpg?v=1759393745",
        "desc": "Polished geometric gold cufflinks with secure bullet-back closures for formal suiting."
    },
    {
        "id": 20,
        "name": "Ares Geometric Gold Studs (Men)",
        "collection": "men",
        "category": "earring",
        "price": 4200,
        "rating": 4.8,
        "reviews": 19,
        "image": "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcTpkIasLyabWjKYMrH03hhNRHikKQbpKMjw-QSwZme3C0_U4yDDF25tSoeYSLCpTiadKJOJJbGjtPYQrwzj1SfikMKYB7IpsGZ3CWD1cpe68D4l3pE0d1zYqg",
        "desc": "Square matte gold stud earrings designed for modern men's ear piercings."
    },

    # --- WEDDING COLLECTION ---
    {
        "id": 30,
        "name": "Royal Polki Sherwani Mala",
        "collection": "wedding",
        "category": "traditional",
        "price": 9950,
        "rating": 5.0,
        "reviews": 64,
        "image": "https://muchmore.co.in/cdn/shop/files/ML-131_3_copy.jpg?v=1771870625&width=352",
        "desc": "An exquisite multi-strand ceremonial mala featuring uncut polki stones and emerald bead drops for groom and wedding attendees."
    },
    {
        "id": 33,
        "name": "Delicate Gold Mangalsutra with Solitaire",
        "collection": "wedding",
        "category": "traditional",
        "price": 9400,
        "rating": 5.0,
        "reviews": 82,
        "image": "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcTFhJWXsCGpqIT6US_NYxRTmhLjduL696tmpZ_vNrx3Nq0Zu5w0nvb02l_uYv75lqm4DjzQKVA36cUKTHKGMqy_tJipXvCsLHnhYd_ImkH3sJQVGs-MGXK4NQ",
        "desc": "Modern minimalist mangalsutra featuring traditional black beads paired with a brilliant lab-grown diamond solitaire pendant."
    },

    # --- MINIMAL COLLECTION ---
    {
        "id": 45,
        "name": "Dainty Gold Anklet with Charms",
        "collection": "minimal",
        "category": "anklets",
        "price": 4500,
        "rating": 4.9,
        "reviews": 48,
        "image": "https://m.media-amazon.com/images/I/411T65p4IeL._SY625_.jpg",
        "desc": "Featherlight 18k gold vermeil anklet featuring tiny dangling star and disc charms."
    },
    {
        "id": 49,
        "name": "Everyday Stacking Plain Band",
        "collection": "minimal",
        "category": "ring",
        "price": 2750,
        "rating": 4.9,
        "reviews": 92,
        "image": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcRzOf9bsaiPfiALjLM0bcZF8h_OoeMdmp1BLfopunrOOdg233WkKm7DoFknMedF82Ri5DlaP28pNutnRol7zsGFHa3H8dEZng",
        "desc": "The ultimate minimalist smooth domed band for effortless everyday stacking."
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
    collection = request.args.get('collection', 'all')
    category = request.args.get('category', 'all')
    search_query = request.args.get('q', '').lower().strip()

    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                query = "SELECT id, name, collection, category, price, rating, reviews, image, desc FROM products WHERE 1=1"
                params = []

                if collection != 'all':
                    query += " AND collection = %s"
                    params.append(collection)
                if category != 'all':
                    query += " AND category = %s"
                    params.append(category)
                if search_query:
                    query += " AND (LOWER(name) LIKE %s OR LOWER(desc) LIKE %s)"
                    params.extend([f"%{search_query}%", f"%{search_query}%"])

                cursor.execute(query, params)
                products = cursor.fetchall()
                conn.close()
                if products:
                    return jsonify(products)
    except Exception as e:
        app.logger.warning(f"Database query failed, serving fallback data. Error: {e}")
        if conn:
            try:
                conn.close()
            except:
                pass

    filtered = FALLBACK_PRODUCTS
    if collection != 'all':
        filtered = [p for p in filtered if p.get('collection') == collection]
    if category != 'all':
        filtered = [p for p in filtered if p.get('category') == category]
    if search_query:
        filtered = [p for p in filtered if search_query in p.get('name', '').lower() or search_query in p.get('desc', '').lower()]

    return jsonify(filtered)

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400
    
    return jsonify({
        "status": "success",
        "user": {
            "name": email.split('@')[0].capitalize(),
            "email": email
        }
    })

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400
    
    return jsonify({
        "status": "success",
        "message": f"Password reset instructions sent to {email}"
    })

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"status": "error", "message": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
