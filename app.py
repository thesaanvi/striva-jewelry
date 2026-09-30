import os
import pymysql
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("AIVEN_DB_HOST", "localhost"),
        port=int(os.getenv("AIVEN_DB_PORT", 3306)),
        user=os.getenv("AIVEN_DB_USER", "root"),
        password=os.getenv("AIVEN_DB_PASSWORD", ""),
        database=os.getenv("AIVEN_DB_NAME", "striva_db"),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ssl": True} if os.getenv("AIVEN_DB_HOST") else None
    )

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "title": "Daily Uniform",
        "subtitle": "When you’re putting together a quick go-to outfit, what’s your baseline vibe?",
        "options": [
            {"label": "Tailored", "text": "Crisp tailored shirt, structured trousers, clean lines.", "tag": "Tailored"},
            {"label": "Relaxed Blazer", "text": "Oversized blazer, relaxed denim, statement sneakers.", "tag": "Oversized Blazer"},
            {"label": "Flowy & Soft", "text": "Flowy silhouette, soft textures, natural tones.", "tag": "Flowy Silhouette"},
            {"label": "Monochrome Edge", "text": "Bold monochrome, sharp cuts, street-style edge.", "tag": "Bold Monochrome"}
        ]
    },
    {
        "id": 2,
        "title": "Stacking & Layering",
        "subtitle": "How do you prefer to wear your neckwear and rings?",
        "options": [
            {"label": "Solo Anchor", "text": "One clean, striking piece and nothing else.", "tag": "Solo Anchor"},
            {"label": "Curated Stack", "text": "2–3 mixed-texture pieces layered together.", "tag": "Curated Stack"},
            {"label": "Delicate Minimalism", "text": "Ultra-thin, barely-there accents.", "tag": "Delicate Minimalism"},
            {"label": "Architectural", "text": "Balanced, geometric pieces with strong proportions.", "tag": "Architectural Symmetry"}
        ]
    },
    {
        "id": 3,
        "title": "Finish & Texture",
        "subtitle": "Which tactile finish catches your eye?",
        "options": [
            {"label": "Mirror Polish", "text": "Ultra-sleek, reflective, completely smooth.", "tag": "High Mirror Polish"},
            {"label": "Brushed / Matte", "text": "Low-key, subtle, understated.", "tag": "Brushed / Matte"},
            {"label": "Hammered / Organic", "text": "Artisanal texture with handcrafted character.", "tag": "Hammered / Organic"},
            {"label": "Two-Tone", "text": "A mix of sterling silver and gold accents.", "tag": "Two-Tone Contrast"}
        ]
    }
]


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/quiz-questions", methods=["GET"])
def get_questions():
    return jsonify({"status": "success", "questions": QUIZ_QUESTIONS})

@app.route("/api/calculate-recommendations", methods=["POST"])
def calculate_recommendations():
    data = request.get_json() or {}
    user_name = data.get("user_name", "Valued Guest").strip() or "Valued Guest"
    preferred_metal = data.get("preferred_metal", "No Preference")
    user_answers = data.get("answers", [])

    user_tags = [ans.get("selected_tag") for ans in user_answers if ans.get("selected_tag")]


    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
    finally:
        conn.close()

    scored_products = []
    for prod in products:
        score = 0
        prod_tags = [t.strip() for t in prod["tags"].split(",") if t.strip()]
        
        if preferred_metal != "No Preference":
            if prod["metal"] == preferred_metal:
                score += 50
            else:
                score -= 10

        tag_matches = set(user_tags).intersection(set(prod_tags))
        score += len(tag_matches) * 15

        scored_products.append({
            "product": {
                "id": prod["id"],
                "name": prod["name"],
                "price": float(prod["price"]),
                "metal": prod["metal"],
                "style_category": prod["style_category"],
                "image_url": prod["image_url"], # URL fetched dynamically from DB
                "description": prod["description"]
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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Striva | Signature Style Quiz</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-alabaster: #FBF9F5;
            --bg-card: #FFFFFF;
            --text-charcoal: #1A1A1A;
            --text-muted: #666666;
            --gold-primary: #C5A059;
            --border-light: #E8E4DC;
            --font-serif: 'Cormorant Garamond', Georgia, serif;
            --font-sans: 'Inter', sans-serif;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: var(--bg-alabaster); color: var(--text-charcoal); font-family: var(--font-sans); }
        
        header { padding: 2rem; text-align: center; border-bottom: 1px solid var(--border-light); }
        .brand-logo { font-family: var(--font-serif); font-size: 2rem; letter-spacing: 0.3em; text-decoration: none; color: var(--text-charcoal); }

        main { max-width: 800px; margin: 3rem auto; padding: 0 1rem; }
        .quiz-card { background: var(--bg-card); border: 1px solid var(--border-light); padding: 2.5rem; }
        
        .intro-title { font-family: var(--font-serif); font-size: 2.5rem; text-align: center; margin-bottom: 1rem; }
        .subtitle { font-size: 1rem; color: var(--text-muted); text-align: center; margin-bottom: 2rem; }

        .btn-primary { width: 100%; padding: 1.2rem; background: var(--text-charcoal); color: white; border: none; font-size: 0.85rem; letter-spacing: 0.2em; text-transform: uppercase; cursor: pointer; }
        .btn-primary:hover { background: var(--gold-primary); }

        .results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .product-card { border: 1px solid var(--border-light); padding: 1rem; text-align: center; background: #fff; }
        
        /* IMAGE STYLING */
        .product-card img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            margin-bottom: 1rem;
        }

        .prod-title { font-family: var(--font-serif); font-size: 1.2rem; margin-bottom: 0.3rem; }
        .prod-price { font-size: 0.95rem; color: var(--gold-primary); font-weight: 500; }
    </style>
</head>
<body>

    <header>
        <a href="#" class="brand-logo">STRIVA</a>
    </header>

    <main>
        <div class="quiz-card" id="quizCard">
            <h1 class="intro-title">Discover Your Signature Edit</h1>
            <p class="subtitle">Complete the quiz to unlock your personalized curation.</p>
            <button class="btn-primary" onclick="loadRecommendations()">View Sample Curation</button>
            
            <div class="results-grid" id="resultsGrid"></div>
        </div>
    </main>

    <script>
        async function loadRecommendations() {
            try {
                const response = await fetch('/api/calculate-recommendations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_name: "Alexander", preferred_metal: "Gold Vermeil", answers: [] })
                });

                const data = await response.json();
                if (data.status === 'success') {
                    const grid = document.getElementById('resultsGrid');
                    grid.innerHTML = '';

                    data.recommendations.forEach(prod => {
                        const prodEl = document.createElement('div');
                        prodEl.className = 'product-card';
                       
                        prodEl.innerHTML = `
                            <img src="${prod.image_url}" alt="${prod.name}" loading="lazy">
                            <div class="prod-title">${prod.name}</div>
                            <div class="prod-price">$${prod.price.toFixed(2)} USD</div>
                        `;
                        grid.appendChild(prodEl);
                    });
                }
            } catch (err) {
                console.error("Error loading curation:", err);
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
