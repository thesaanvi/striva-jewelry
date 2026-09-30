import os
import pymysql
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Fallback product list if Aiven DB is empty or connecting fails
FALLBACK_PRODUCTS = [
    {
        "id": "striva-001",
        "name": "The Heritage Signet Ring",
        "price": 11999.00,
        "metal": "Gold Vermeil",
        "style_category": "Classic",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&q=80&w=600",
        "tags": "Tailored, High Mirror Polish, Solo Anchor, Everyday"
    },
    {
        "id": "striva-002",
        "name": "Architectural Bar Pendant",
        "price": 14499.00,
        "metal": "Sterling Silver",
        "style_category": "Modern",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&q=80&w=600",
        "tags": "Oversized Blazer, Brushed / Matte, Curated Stack"
    },
    {
        "id": "striva-003",
        "name": "Organic Ripple Cuff",
        "price": 16999.00,
        "metal": "Gold Vermeil",
        "style_category": "Artisanal",
        "image_url": "https://images.unsplash.com/photo-1611591475155-4286fa7c2e7f?auto=format&fit=crop&q=80&w=600",
        "tags": "Hammered / Organic, Flowy Silhouette, Architectural Symmetry"
    }
]

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "title": "Daily Uniform",
        "subtitle": "When putting together a quick go-to outfit, what is your baseline aesthetic?",
        "options": [
            {"label": "Tailored & Sharp", "text": "Crisp shirts, structured trousers, clean lines.", "tag": "Tailored"},
            {"label": "Relaxed & Layered", "text": "Oversized blazers, soft knits, street-style comfort.", "tag": "Oversized Blazer"},
            {"label": "Flowy & Natural", "text": "Organic textures, breathable silhouettes, soft tones.", "tag": "Flowy Silhouette"},
            {"label": "Monochrome Edge", "text": "Bold black and white, sharp geometric cuts.", "tag": "Bold Monochrome"}
        ]
    },
    {
        "id": 2,
        "title": "Stacking & Layering",
        "subtitle": "How do you prefer to style your neckwear and rings?",
        "options": [
            {"label": "Solo Anchor Piece", "text": "One clean, striking piece and nothing else.", "tag": "Solo Anchor"},
            {"label": "Curated Stack", "text": "2–3 mixed-texture pieces layered together effortlessly.", "tag": "Curated Stack"},
            {"label": "Barely-There Minimal", "text": "Ultra-thin chains and delicate subtle accents.", "tag": "Delicate Minimalism"},
            {"label": "Architectural Statement", "text": "Geometric designs with strong physical presence.", "tag": "Architectural Symmetry"}
        ]
    },
    {
        "id": 3,
        "title": "Finish & Tactile Texture",
        "subtitle": "Which metal texture catches your eye first?",
        "options": [
            {"label": "High Mirror Polish", "text": "Ultra-sleek, reflective, and completely liquid-smooth.", "tag": "High Mirror Polish"},
            {"label": "Brushed / Matte", "text": "Understated, subtle, and low-glare elegance.", "tag": "Brushed / Matte"},
            {"label": "Hammered / Organic", "text": "Artisanal texture with handcrafted raw character.", "tag": "Hammered / Organic"},
            {"label": "Two-Tone Contrast", "text": "Seamless blend of Sterling Silver and Gold Vermeil.", "tag": "Two-Tone Contrast"}
        ]
    },
    {
        "id": 4,
        "title": "Occasion & Presence",
        "subtitle": "Where are you primarily wearing your Striva pieces?",
        "options": [
            {"label": "Everyday Everyday", "text": "Durable, versatile pieces suitable for work and daily life.", "tag": "Everyday"},
            {"label": "Evening & Statement", "text": "Elevated designs made for dinners and evening events.", "tag": "Evening"},
            {"label": "Artistic Expression", "text": "Unique, conversation-starting sculptural jewelry.", "tag": "Sculptural"}
        ]
    },
    {
        "id": 5,
        "title": "Proportions & Weight",
        "subtitle": "What scale of jewelry feels most natural against your skin?",
        "options": [
            {"label": "Featherlight & Fine", "text": "Subtle pieces that you forget you're wearing.", "tag": "Fine Scale"},
            {"label": "Medium Sculptural Balance", "text": "Noticeable weight that adds intentional structure.", "tag": "Medium Scale"},
            {"label": "Heavyweight Solid", "text": "Substantial, solid precious metals with tactile gravity.", "tag": "Heavy Scale"}
        ]
    }
]

def get_db_connection():
    # Only try connecting if environment variables are provided
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
    # Renders index.html from your templates directory or directly if using template string
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "index.html file not found in root directory!", 404

@app.route("/api/quiz-questions", methods=["GET"])
def get_questions():
    return jsonify({"status": "success", "questions": QUIZ_QUESTIONS})

@app.route("/api/calculate-recommendations", methods=["POST"])
def calculate_recommendations():
    try:
        data = request.get_json() or {}
        user_name = data.get("user_name", "Valued Guest").strip() or "Valued Guest"
        preferred_metal = data.get("preferred_metal", "No Preference")
        user_answers = data.get("answers", [])

        user_tags = [ans.get("selected_tag") for ans in user_answers if ans.get("selected_tag")]

        products = []
        conn = None
        
        # Safe DB Fetch
        try:
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM products")
                    products = cursor.fetchall()
        except Exception as db_err:
            print(f"Database connection error: {db_err}")
        finally:
            if conn:
                conn.close()

        # Fallback if DB fetch returned nothing or failed
        if not products:
            products = FALLBACK_PRODUCTS

        scored_products = []
        for prod in products:
            score = 0
            prod_tags = [t.strip() for t in prod.get("tags", "").split(",") if t.strip()]
            
            if preferred_metal != "No Preference":
                if prod.get("metal") == preferred_metal:
                    score += 50

            tag_matches = set(user_tags).intersection(set(prod_tags))
            score += len(tag_matches) * 15

            scored_products.append({
                "product": {
                    "id": prod.get("id"),
                    "name": prod.get("name"),
                    "price": float(prod.get("price", 0)),
                    "metal": prod.get("metal", "Gold Vermeil"),
                    "style_category": prod.get("style_category", "Classic"),
                    "image_url": prod.get("image_url", ""),
                    "description": prod.get("description", "")
                },
                "score": score
            })

        scored_products.sort(key=lambda x: x["score"], reverse=True)
        top_edits = [item["product"] for item in scored_products[:3]]

        return jsonify({
            "status": "success",
            "user_name": user_name,
            "archetype": "The Modern Minimalist",
            "metal_preference": preferred_metal,
            "recommendations": top_edits
        })
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
