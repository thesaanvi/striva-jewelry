import os
import pymysql
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Complete Product Catalog (>20 products across all requested categories & filters)
CATALOG_PRODUCTS = [
    # EVERYDAY / MINIMAL / WOMEN
    {
        "id": "str-w-001",
        "name": "The Celestial Signet Ring",
        "price": 3499.00,
        "metal": "Gold Vermeil",
        "category": "women",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&q=80&w=600",
        "tags": "Tailored, High Mirror Polish, Solo Anchor, Everyday"
    },
    {
        "id": "str-w-002",
        "name": "Liquid Gold Herringbone Chain",
        "price": 4999.00,
        "metal": "Gold Vermeil",
        "category": "women",
        "style": "minimal",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&q=80&w=600",
        "tags": "Curated Stack, High Mirror Polish, Delicate Minimalism"
    },
    {
        "id": "str-w-003",
        "name": "Sculptural Ripple Hoop Earrings",
        "price": 2899.00,
        "metal": "Gold Vermeil",
        "category": "women",
        "style": "minimal",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&q=80&w=600",
        "tags": "Hammered / Organic, Medium Scale, Everyday"
    },
    {
        "id": "str-w-004",
        "name": "Minimalist Solitaire Tennis Bracelet",
        "price": 5499.00,
        "metal": "Sterling Silver",
        "category": "women",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1611591475155-4286fa7c2e7f?auto=format&fit=crop&q=80&w=600",
        "tags": "Delicate Minimalism, Fine Scale, Everyday"
    },
    {
        "id": "str-w-005",
        "name": "Architectural Geometric Bar Pendant",
        "price": 3899.00,
        "metal": "Sterling Silver",
        "category": "women",
        "style": "minimal",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=600",
        "tags": "Architectural Symmetry, Brushed / Matte, Solo Anchor"
    },
    {
        "id": "str-w-006",
        "name": "Bespoke Interlocking Daily Band",
        "price": 2499.00,
        "metal": "Gold Vermeil",
        "category": "women",
        "style": "minimal",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&q=80&w=600",
        "tags": "Tailored, Everyday, Medium Scale"
    },
    {
        "id": "str-w-007",
        "name": "Petite Emerald Cut Drop Pendant",
        "price": 4299.00,
        "metal": "Gold Vermeil",
        "category": "women",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&q=80&w=600",
        "tags": "Evening, Solo Anchor, High Mirror Polish"
    },

    # MEN'S COLLECTION
    {
        "id": "str-m-001",
        "name": "Heavyweight Cuban Link Chain",
        "price": 6999.00,
        "metal": "Sterling Silver",
        "category": "men",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1588444839799-eb00f4904658?auto=format&fit=crop&q=80&w=600",
        "tags": "Heavy Scale, Solo Anchor, Brushed / Matte"
    },
    {
        "id": "str-m-002",
        "name": "Brushed Matte Octagon Signet",
        "price": 3299.00,
        "metal": "Sterling Silver",
        "category": "men",
        "style": "minimal",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1622398925373-3f91b1e275f5?auto=format&fit=crop&q=80&w=600",
        "tags": "Architectural Symmetry, Brushed / Matte, Tailored"
    },
    {
        "id": "str-m-003",
        "name": "Obsidian & Vermeil Cuff Bracelet",
        "price": 4899.00,
        "metal": "Gold Vermeil",
        "category": "men",
        "style": "minimal",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1611591475155-4286fa7c2e7f?auto=format&fit=crop&q=80&w=600",
        "tags": "Bold Monochrome, Heavy Scale, Statement"
    },
    {
        "id": "str-m-004",
        "name": "Beveled Edged Band",
        "price": 2799.00,
        "metal": "Sterling Silver",
        "category": "men",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&q=80&w=600",
        "tags": "Tailored, Everyday, Medium Scale"
    },
    {
        "id": "str-m-005",
        "name": "Tactile Hammered Dog Tag Pendant",
        "price": 4199.00,
        "metal": "Sterling Silver",
        "category": "men",
        "style": "minimal",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=600",
        "tags": "Hammered / Organic, Solo Anchor, Medium Scale"
    },
    {
        "id": "str-m-006",
        "name": "Textured Cable Rope Chain",
        "price": 5299.00,
        "metal": "Gold Vermeil",
        "category": "men",
        "style": "minimal",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&q=80&w=600",
        "tags": "Curated Stack, Heavy Scale, High Mirror Polish"
    },
    {
        "id": "str-m-007",
        "name": "Sleek Minimalist Money Clip",
        "price": 1999.00,
        "metal": "Sterling Silver",
        "category": "men",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1622398925373-3f91b1e275f5?auto=format&fit=crop&q=80&w=600",
        "tags": "Tailored, Brushed / Matte, Fine Scale"
    },

    # COUPLE / UNISEX COLLECTION
    {
        "id": "str-c-001",
        "name": "Eternal Bond Matching Bands",
        "price": 5999.00,
        "metal": "Two-Tone",
        "category": "couple",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&q=80&w=600",
        "tags": "Two-Tone Contrast, Everyday, Tailored"
    },
    {
        "id": "str-c-002",
        "name": "Dual Meridian Pendant Set",
        "price": 7499.00,
        "metal": "Gold Vermeil",
        "category": "couple",
        "style": "minimal",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=600",
        "tags": "Curated Stack, Solo Anchor, Medium Scale"
    },
    {
        "id": "str-c-003",
        "name": "Symmetrical Infinity Cuffs (Pair)",
        "price": 8299.00,
        "metal": "Sterling Silver",
        "category": "couple",
        "style": "minimal",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1611591475155-4286fa7c2e7f?auto=format&fit=crop&q=80&w=600",
        "tags": "Architectural Symmetry, High Mirror Polish, Heavy Scale"
    },
    {
        "id": "str-c-004",
        "name": "Engraved Coordinates Secret Ring Set",
        "price": 6499.00,
        "metal": "Gold Vermeil",
        "category": "couple",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&q=80&w=600",
        "tags": "Tailored, Delicate Minimalism, Everyday"
    },
    {
        "id": "str-c-005",
        "name": "Yin-Yang Sculptural Medallions",
        "price": 6899.00,
        "metal": "Two-Tone",
        "category": "couple",
        "style": "minimal",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&q=80&w=600",
        "tags": "Two-Tone Contrast, Sculptural, Medium Scale"
    },
    {
        "id": "str-c-006",
        "name": "Minimalist Anchor Link Bracelets",
        "price": 5199.00,
        "metal": "Sterling Silver",
        "category": "couple",
        "style": "minimal",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1588444839799-eb00f4904658?auto=format&fit=crop&q=80&w=600",
        "tags": "Curated Stack, Everyday, Brushed / Matte"
    },
    {
        "id": "str-c-007",
        "name": "Solstice Matching Bar Necklaces",
        "price": 7299.00,
        "metal": "Gold Vermeil",
        "category": "couple",
        "style": "minimal",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&q=80&w=600",
        "tags": "Architectural Symmetry, High Mirror Polish, Solo Anchor"
    },

    # TRADITIONAL DEMI-FINE WEDDING COLLECTION (Minimum 5 Items)
    {
        "id": "str-wed-001",
        "name": "Royale Kundan-Dipped Choker Set",
        "price": 18999.00,
        "metal": "Gold Vermeil",
        "category": "wedding",
        "style": "wedding",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&q=80&w=600",
        "tags": "Evening, Heavy Scale, Sculptural"
    },
    {
        "id": "str-wed-002",
        "name": "Heritage Emerald Polki Statement Necklace",
        "price": 24999.00,
        "metal": "Gold Vermeil",
        "category": "wedding",
        "style": "wedding",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&q=80&w=600",
        "tags": "Evening, Heavy Scale, Statement"
    },
    {
        "id": "str-wed-003",
        "name": "Artisanal Chandbali Hoop Earrings",
        "price": 8999.00,
        "metal": "Gold Vermeil",
        "category": "wedding",
        "style": "wedding",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&q=80&w=600",
        "tags": "Hammered / Organic, Evening, Sculptural"
    },
    {
        "id": "str-wed-004",
        "name": "Temple Filigree Bridal Kada (Set of 2)",
        "price": 15499.00,
        "metal": "Gold Vermeil",
        "category": "wedding",
        "style": "wedding",
        "collection": "bestseller",
        "image_url": "https://images.unsplash.com/photo-1611591475155-4286fa7c2e7f?auto=format&fit=crop&q=80&w=600",
        "tags": "Evening, Heavy Scale, Two-Tone Contrast"
    },
    {
        "id": "str-wed-005",
        "name": "Solitaire Kundan Maang Tikka",
        "price": 5999.00,
        "metal": "Gold Vermeil",
        "category": "wedding",
        "style": "wedding",
        "collection": "curator_fav",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&q=80&w=600",
        "tags": "Solo Anchor, Fine Scale, Evening"
    },
    {
        "id": "str-wed-006",
        "name": "Imperial Pearl & Kundan Layered Mala",
        "price": 21999.00,
        "metal": "Gold Vermeil",
        "category": "wedding",
        "style": "wedding",
        "collection": "trending",
        "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=600",
        "tags": "Curated Stack, Heavy Scale, Sculptural"
    }
]

# 8 Valid, In-Depth Quiz Questions
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "title": "Aesthetic Baseline",
        "subtitle": "When styling a quick go-to look, what is your baseline fashion direction?",
        "options": [
            {"label": "Tailored & Sharp", "text": "Structured suits, crisp collars, tailored trousers.", "tag": "Tailored"},
            {"label": "Relaxed & Layered", "text": "Oversized blazers, soft street-style knits, easy layering.", "tag": "Oversized Blazer"},
            {"label": "Flowy & Natural", "text": "Organic textures, breezy silhouettes, earth tones.", "tag": "Flowy Silhouette"},
            {"label": "Monochrome Edge", "text": "High-contrast black & white, geometric cuts.", "tag": "Bold Monochrome"}
        ]
    },
    {
        "id": 2,
        "title": "Stacking & Layering",
        "subtitle": "How do you naturally balance your jewelry daily?",
        "options": [
            {"label": "Solo Anchor Piece", "text": "One central, striking piece and minimal distraction.", "tag": "Solo Anchor"},
            {"label": "Curated Stack", "text": "2-3 mixed-texture pieces layered thoughtfully.", "tag": "Curated Stack"},
            {"label": "Barely-There Minimal", "text": "Ultra-thin, featherlight chains and subtle accents.", "tag": "Delicate Minimalism"},
            {"label": "Architectural Statement", "text": "Bold geometric designs with heavy physical presence.", "tag": "Architectural Symmetry"}
        ]
    },
    {
        "id": 3,
        "title": "Finish & Tactile Character",
        "subtitle": "Which metal surface finish captures your eye first?",
        "options": [
            {"label": "High Mirror Polish", "text": "Ultra-sleek, liquid-smooth, and intensely reflective.", "tag": "High Mirror Polish"},
            {"label": "Brushed / Matte", "text": "Understated, muted, low-glare contemporary look.", "tag": "Brushed / Matte"},
            {"label": "Hammered / Organic", "text": "Raw handcrafted character with artisanal indentations.", "tag": "Hammered / Organic"},
            {"label": "Two-Tone Contrast", "text": "Seamless mixture of 18k Gold Vermeil and 925 Silver.", "tag": "Two-Tone Contrast"}
        ]
    },
    {
        "id": 4,
        "title": "Primary Wear Setting",
        "subtitle": "Where will your new Striva pieces see the most wear?",
        "options": [
            {"label": "Work & Everyday", "text": "Durable, comfortable pieces for meetings and daily routines.", "tag": "Everyday"},
            {"label": "Evening & Dinners", "text": "Elevated accents crafted for nightlife and special occasions.", "tag": "Evening"},
            {"label": "Weddings & Celebrations", "text": "Grand traditional demi-fine pieces with rich heritage details.", "tag": "Wedding"},
            {"label": "Artistic Expression", "text": "Unique conversation-starters for modern gallery spaces.", "tag": "Sculptural"}
        ]
    },
    {
        "id": 5,
        "title": "Scale & Visual Weight",
        "subtitle": "What size profile feels most natural against your skin?",
        "options": [
            {"label": "Featherlight & Delicate", "text": "Whisper-thin scale you completely forget you're wearing.", "tag": "Fine Scale"},
            {"label": "Medium Sculptural Balance", "text": "Noticeable weight that lends intentional structure.", "tag": "Medium Scale"},
            {"label": "Heavyweight Solid Metal", "text": "Substantial, solid precious metals with physical gravity.", "tag": "Heavy Scale"}
        ]
    },
    {
        "id": 6,
        "title": "Core Metal Loyalty",
        "subtitle": "Which precious metal tone harmonizes best with your skin tone?",
        "options": [
            {"label": "Warm 18k Gold Vermeil", "text": "Rich, sun-kissed 2.5-micron gold layer over sterling silver.", "tag": "Gold Vermeil"},
            {"label": "Cool Recycled 925 Silver", "text": "Crisp, bright silver finished with anti-tarnish rhodium.", "tag": "Sterling Silver"},
            {"label": "Mixed Metal Alchemy", "text": "I love wearing gold and silver in the same stack.", "tag": "Two-Tone"}
        ]
    },
    {
        "id": 7,
        "title": "Intentionality & Purpose",
        "subtitle": "Who are you selecting this piece for today?",
        "options": [
            {"label": "Personal Daily Signature", "text": "Treating myself to an upgraded daily wardrobe staple.", "tag": "Self-Reward"},
            {"label": "Couple / Matching Sets", "text": "Searching for complementary pieces for me and my partner.", "tag": "Couple"},
            {"label": "Unforgettable Gift", "text": "Surprising someone special with luxury packaging.", "tag": "Gifting"}
        ]
    },
    {
        "id": 8,
        "title": "Investment Tier",
        "subtitle": "What budget spectrum fits your current wardrobe expansion plan?",
        "options": [
            {"label": "Essential Staples (₹2,000 - ₹5,000)", "text": "Versatile daily pieces built for high durability.", "tag": "Tier1"},
            {"label": "Elevated Curations (₹5,000 - ₹12,000)", "text": "Substantial multi-gem or heavy metal designs.", "tag": "Tier2"},
            {"label": "Heritage & Bridal (₹12,000+)", "text": "Intricate traditional demi-fine statement sets.", "tag": "Tier3"}
        ]
    }
]

def get_db_connection():
    host = os.getenv("AIVEN_DB_HOST")
    if not host:
        return None
    return pymysql.connect(
        host=host,
        port=int(os.getenv("AIVEN_DB_PORT", 3306)),
        user=os.getenv("AIVEN_DB_USER", "root"),
        password=os.getenv("AIVEN_DB_PASSWORD", ""),
        database=os.getenv("AIVEN_DB_NAME", "defaultdb"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=3,
        ssl={"ssl": True}
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/products", methods=["GET"])
def get_products():
    category = request.args.get("category")
    style = request.args.get("style")
    collection = request.args.get("collection")

    # DB Fetch attempt with automatic fallback to static CATALOG_PRODUCTS
    products = []
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM products")
                products = cursor.fetchall()
    except Exception:
        pass
    finally:
        if conn:
            conn.close()

    if not products:
        products = CATALOG_PRODUCTS

    filtered = products
    if category and category != 'all':
        filtered = [p for p in filtered if p.get("category") == category]
    if style and style != 'all':
        filtered = [p for p in filtered if p.get("style") == style]
    if collection and collection != 'all':
        filtered = [p for p in filtered if p.get("collection") == collection]

    return jsonify({"status": "success", "products": filtered})

@app.route("/api/quiz-questions", methods=["GET"])
def get_questions():
    return jsonify({"status": "success", "questions": QUIZ_QUESTIONS})

@app.route("/api/calculate-recommendations", methods=["POST"])
def calculate_recommendations():
    try:
        data = request.get_json() or {}
        user_name = data.get("user_name", "Valued Guest").strip() or "Valued Guest"
        user_answers = data.get("answers", [])

        user_tags = [ans.get("selected_tag") for ans in user_answers if ans.get("selected_tag")]

        scored_products = []
        for prod in CATALOG_PRODUCTS:
            score = 0
            prod_tags = [t.strip() for t in prod.get("tags", "").split(",") if t.strip()]
            tag_matches = set(user_tags).intersection(set(prod_tags))
            score += len(tag_matches) * 20

            if "Gold Vermeil" in user_tags and prod.get("metal") == "Gold Vermeil":
                score += 30
            elif "Sterling Silver" in user_tags and prod.get("metal") == "Sterling Silver":
                score += 30

            scored_products.append({"product": prod, "score": score})

        scored_products.sort(key=lambda x: x["score"], reverse=True)
        top_edits = [item["product"] for item in scored_products[:4]]

        return jsonify({
            "status": "success",
            "user_name": user_name,
            "archetype": "The Modern Architecturalist",
            "recommendations": top_edits
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
