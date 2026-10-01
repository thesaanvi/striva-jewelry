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

# Expanded catalog (~50 items) with accurate pricing (₹999 to ₹10,000 INR) and specific category product images
FALLBACK_PRODUCTS = [
    # --- TRENDING (Women Minimal & Wedding) ---
    {
        "id": 1, "name": "Aura Solitaire Diamond Ring", "gender": "female", "occasion": "minimal", "category": "rings", "price": 1499, "section": "trending", 
        "image": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcTaoqyh1mcAd6fwebKjWgs7BwqTiUGd6MaCNzL25tbFVOIEJ3Mx",
        "description": "Crafted in 18k gold vermeil with a brilliant-cut solitaire diamond centerpiece. Designed for everyday grace and effortless layering."
    },
    {
        "id": 2, "name": "Kundan Floral Nose Ring", "gender": "female", "occasion": "wedding", "category": "nosering", "price": 1999, "section": "trending", 
        "image": "https://silvertrendy.in/wp-content/uploads/2024/10/ChatGPT-Image-Sep-12-2026-06_07_42-PM.png",
        "description": "Traditional Kundan craftsmanship meets lightweight modern wear. Perfect for bridal grandeur and festive celebrations."
    },
    {
        "id": 3, "name": "Sleek Titanium Men's Band", "gender": "male", "occasion": "minimal", "category": "rings", "price": 1899, "section": "trending", 
        "image": "https://images.unsplash.com/photo-1603561596112-0a132b757442?w=500&q=80",
        "description": "Matte-finished titanium ring engineered for rugged daily wear with a touch of understated luxury."
    },
    {
        "id": 4, "name": "Forever Love Matching Couple Bands", "gender": "couple", "occasion": "wedding", "category": "rings", "price": 4499, "section": "trending", 
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80",
        "description": "Interlocking dual-tone rings symbolic of eternal commitment. Custom engraving available."
    },
    {
        "id": 5, "name": "Opulent Polki Chandelier Earrings", "gender": "female", "occasion": "wedding", "category": "earrings", "price": 7499, "section": "trending", 
        "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80",
        "description": "Intricately handcrafted earrings set with sparkling Polki stones and dangling pearl drops."
    },

    # --- BEST SELLERS ---
    {
        "id": 6, "name": "Elegance Pearl Layered Necklace", "gender": "female", "occasion": "minimal", "category": "necklace chain", "price": 2499, "section": "best_sellers", 
        "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80",
        "description": "Double-strand freshwater pearls suspended on a 925 sterling silver gold-plated chain."
    },
    {
        "id": 7, "name": "18k Gold Vermeil Mangalsutra", "gender": "female", "occasion": "wedding", "category": "mangalsutra", "price": 5999, "section": "best_sellers", 
        "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80",
        "description": "Modern lightweight mangalsutra featuring black beads and a diamond-studded geometric pendant."
    },
    {
        "id": 8, "name": "Classic Heavy Men's Gold Chain", "gender": "male", "occasion": "wedding", "category": "necklace chain", "price": 6999, "section": "best_sellers", 
        "image": "https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=500&q=80",
        "description": "Bold curb chain crafted with durable 18k yellow gold plating over stainless steel core."
    },
    {
        "id": 9, "name": "Dual Promise Key-Lock Pendants", "gender": "couple", "occasion": "minimal", "category": "necklace chain", "price": 3199, "section": "best_sellers", 
        "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80",
        "description": "Matching his-and-hers lock and key pendant necklaces designed for couples."
    },
    {
        "id": 10, "name": "Minimalist Geometric Cuff Bracelet", "gender": "female", "occasion": "minimal", "category": "bracelets", "price": 2199, "section": "best_sellers", 
        "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80",
        "description": "Sleek open cuff with polished gold finish, perfect for stacking with watches."
    },

    # --- CURATOR'S CHOICE ---
    {
        "id": 11, "name": "Crystal Charm Silver Anklet", "gender": "female", "occasion": "minimal", "category": "anklets", "price": 1299, "section": "curators_choice", 
        "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80",
        "description": "Delicate sterling silver anklet accented with shimmering cubic zirconia stations."
    },
    {
        "id": 12, "name": "Royal Emerald Maang Tikka", "gender": "female", "occasion": "wedding", "category": "mang tikka", "price": 4999, "section": "curators_choice", 
        "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80",
        "description": "Statement maang tikka featuring a central simulated emerald surrounded by polki diamonds."
    },
    {
        "id": 13, "name": "Cuban Link Men's Bracelet", "gender": "male", "occasion": "minimal", "category": "bracelets", "price": 2299, "section": "curators_choice", 
        "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80",
        "description": "Robust and masculine Cuban link bracelet with secure box clasp lock."
    },
    {
        "id": 14, "name": "Regal Emerald Cut Cocktail Ring", "gender": "female", "occasion": "wedding", "category": "rings", "price": 3899, "section": "curators_choice", 
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80",
        "description": "An eye-catching emerald-cut gemstone ring flanked by micro-pavé halo stones."
    },
    {
        "id": 15, "name": "Infinity Eternal Couple Bracelets", "gender": "couple", "occasion": "minimal", "category": "bracelets", "price": 2799, "section": "curators_choice", 
        "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80",
        "description": "Braided leather and stainless steel bracelets featuring an infinity connector."
    },

    # --- ADDITIONAL SEED ITEMS ---
    { "id": 16, "name": "Daily Sparkle Stud Earrings", "gender": "female", "occasion": "minimal", "category": "earrings", "price": 999, "section": "trending", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80", "description": "Subtle solitaire studs for everyday office wear." },
    { "id": 17, "name": "Pearl Drop Bridal Earrings", "gender": "female", "occasion": "wedding", "category": "earrings", "price": 3499, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80", "description": "Graceful baroque pearl drop earrings." },
    { "id": 18, "name": "Men's Onyx Signet Ring", "gender": "male", "occasion": "minimal", "category": "rings", "price": 2599, "section": "trending", "image": "https://images.unsplash.com/photo-1603561596112-0a132b757442?w=500&q=80", "description": "Vintage style black onyx signet ring in silver." },
    { "id": 19, "name": "Navratna Traditional Bangles Set", "gender": "female", "occasion": "wedding", "category": "bracelets", "price": 8999, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80", "description": "Set of 4 gold-plated bangles inlaid with precious multi-color gemstones." },
    { "id": 20, "name": "Minimalist Heart Locket Necklace", "gender": "female", "occasion": "minimal", "category": "necklace chain", "price": 1799, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Tiny open heart locket that holds a miniature photo." },
    { "id": 21, "name": "Groom's Sherwani Brooch", "gender": "male", "occasion": "wedding", "category": "brooch", "price": 3999, "section": "trending", "image": "https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=500&q=80", "description": "Royal pearl and kundan brooch pin for ethnic menswear." },
    { "id": 22, "name": "Couple Initials Engraved Pendant", "gender": "couple", "occasion": "minimal", "category": "necklace chain", "price": 2999, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Customizable disk pendant with entwined initials." },
    { "id": 23, "name": "Temple Heritage Jhumkas", "gender": "female", "occasion": "wedding", "category": "earrings", "price": 5499, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80", "description": "South Indian temple art inspired gold jhumka earrings." },
    { "id": 24, "name": "Sleek Silver Toe Rings (Pair)", "gender": "female", "occasion": "wedding", "category": "rings", "price": 1199, "section": "trending", "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80", "description": "Adjustable sterling silver toe rings with floral engraving." },
    { "id": 25, "name": "Men's Braided Leather Bracelet", "gender": "male", "occasion": "minimal", "category": "bracelets", "price": 1599, "section": "trending", "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80", "description": "Genuine black leather wrap bracelet with magnetic steel lock." },
    { "id": 26, "name": "Zircon Tennis Bracelet", "gender": "female", "occasion": "minimal", "category": "bracelets", "price": 4299, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80", "description": "Continuous line of sparkling round cubic zirconia stones." },
    { "id": 27, "name": "Bridal Hathphool Hand Harness", "gender": "female", "occasion": "wedding", "category": "bracelets", "price": 6499, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80", "description": "Delicate chain bracelet connected to an ethnic finger ring." },
    { "id": 28, "name": "Minimalist Bar Necklace", "gender": "female", "occasion": "minimal", "category": "necklace chain", "price": 1699, "section": "trending", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Horizontal curved metallic bar suspended on a fine chain." },
    { "id": 29, "name": "Men's Cufflinks & Tie Pin Set", "gender": "male", "occasion": "wedding", "category": "accessories", "price": 2899, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=500&q=80", "description": "Polished silver-tone formal wear accessory set." },
    { "id": 30, "name": "Matching Soulmate Bands", "gender": "couple", "occasion": "wedding", "category": "rings", "price": 4999, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80", "description": "Matching gold vermeil wedding bands with brushed center." },
    { "id": 31, "name": "Dainty Butterfly Anklet", "gender": "female", "occasion": "minimal", "category": "anklets", "price": 1399, "section": "trending", "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80", "description": "Cute butterfly charms dangling on a lightweight chain." },
    { "id": 32, "name": "Polki Statement Choker", "gender": "female", "occasion": "wedding", "category": "necklace chain", "price": 9999, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Grand bridal choker necklace with dangling pearls." },
    { "id": 33, "name": "Men's Minimalist Cross Pendant", "gender": "male", "occasion": "minimal", "category": "necklace chain", "price": 1999, "section": "trending", "image": "https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=500&q=80", "description": "Clean-cut stainless steel cross pendant on a box chain." },
    { "id": 34, "name": "Layered Coin Necklace", "gender": "female", "occasion": "minimal", "category": "necklace chain", "price": 2599, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Multi-tier coin medallion necklace in 18k gold finish." },
    { "id": 35, "name": "Traditional Nath with Chain", "gender": "female", "occasion": "wedding", "category": "nosering", "price": 2299, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&q=80", "description": "Bridal clip-on nose ring with support chain." },
    { "id": 36, "name": "Couple Puzzle Piece Pendants", "gender": "couple", "occasion": "minimal", "category": "necklace chain", "price": 2499, "section": "trending", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Interlocking puzzle piece necklaces that fit together." },
    { "id": 37, "name": "Pearl Studded Matha Patti", "gender": "female", "occasion": "wedding", "category": "mang tikka", "price": 5999, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80", "description": "Royal head ornament framing the forehead beautifully." },
    { "id": 38, "name": "Sleek Snake Chain Bracelet", "gender": "female", "occasion": "minimal", "category": "bracelets", "price": 1899, "section": "trending", "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80", "description": "Fluid snake chain bracelet that hugs the wrist." },
    { "id": 39, "name": "Men's Tiger Eye Stone Ring", "gender": "male", "occasion": "minimal", "category": "rings", "price": 2399, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1603561596112-0a132b757442?w=500&q=80", "description": "Natural tiger eye gemstone set in a heavy band." },
    { "id": 40, "name": "Minimalist Hoop Earrings", "gender": "female", "occasion": "minimal", "category": "earrings", "price": 1299, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80", "description": "Lightweight everyday medium gold hoops." },
    { "id": 41, "name": "Royal Ruby Bridal Set", "gender": "female", "occasion": "wedding", "category": "necklace chain", "price": 9499, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Matching ruby necklace and earrings wedding set." },
    { "id": 42, "name": "Couple Infinity Rings", "gender": "couple", "occasion": "minimal", "category": "rings", "price": 3299, "section": "trending", "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80", "description": "Infinity engraved matching bands for partners." },
    { "id": 43, "name": "Silver Ghungroo Anklet", "gender": "female", "occasion": "wedding", "category": "anklets", "price": 1999, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80", "description": "Traditional melodious bell anklets in pure silver finish." },
    { "id": 44, "name": "Men's Black Steel Watch Chain", "gender": "male", "occasion": "minimal", "category": "bracelets", "price": 2799, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80", "description": "Matte black stainless steel link bracelet." },
    { "id": 45, "name": "Geometric Drop Earrings", "gender": "female", "occasion": "minimal", "category": "earrings", "price": 1599, "section": "trending", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80", "description": "Contemporary minimalist geometric gold drops." },
    { "id": 46, "name": "Lightweight Bridal Mangalsutra", "gender": "female", "occasion": "wedding", "category": "mangalsutra", "price": 4599, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80", "description": "Dainty daily wear mangalsutra for modern brides." },
    { "id": 47, "name": "Couple Sun & Moon Necklaces", "gender": "couple", "occasion": "minimal", "category": "necklace chain", "price": 2899, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Sun and moon matching celestial pendant necklaces." },
    { "id": 48, "name": "Classic Pearl Studs", "gender": "female", "occasion": "minimal", "category": "earrings", "price": 1099, "section": "trending", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80", "description": "Single-stone pearl studs for clean elegance." },
    { "id": 49, "name": "Men's Gold Plated Kara", "gender": "male", "occasion": "wedding", "category": "bracelets", "price": 3499, "section": "best_sellers", "image": "https://images.unsplash.com/photo-1611591475253-5d1f4d2f45f7?w=500&q=80", "description": "Classic thick polished steel kara with gold plating." },
    { "id": 50, "name": "Bespoke Custom Name Pendant", "gender": "female", "occasion": "minimal", "category": "necklace chain", "price": 3199, "section": "curators_choice", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80", "description": "Customized nameplate cursive script necklace." }
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
