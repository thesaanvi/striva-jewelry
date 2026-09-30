from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Sample Product Database with standard demi-fine pricing
PRODUCTS = [
    # Female / General
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
        "name": "Royal Emerald Maang Tikka",
        "gender": "female",
        "occasion": "wedding",
        "category": "mang tikka",
        "price": 4999,
        "section": "curators_choice",
        "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80"
    },
    {
        "id": 4,
        "name": "Kundan Floral Nose Ring",
        "gender": "female",
        "occasion": "wedding",
        "category": "nosering",
        "price": 1999,
        "section": "trending",
        "image": "https://images.unsplash.com/photo-1611591475879-88001e19488a?w=500&q=80"
    },
    {
        "id": 5,
        "name": "18k Gold Vermeil Mangalsutra",
        "gender": "female",
        "occasion": "wedding",
        "category": "mangalsutra",
        "price": 5999,
        "section": "best_sellers",
        "image": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=500&q=80"
    },
    {
        "id": 6,
        "name": "Crystal Charm Silver Anklet",
        "gender": "female",
        "occasion": "minimal",
        "category": "anklets",
        "price": 1299,
        "section": "curators_choice",
        "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80"
    },
    # Male Section
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
    # Couple Section
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

@app.route('/api/products', methods=['GET'])
def get_products():
    gender = request.args.get('gender', 'all')
    occasion = request.args.get('occasion', 'all')
    category = request.args.get('category', 'all')
    section = request.args.get('section', 'all')

    filtered = PRODUCTS

    if gender != 'all':
        filtered = [p for p in filtered if p['gender'] == gender]
    if occasion != 'all':
        filtered = [p for p in filtered if p['occasion'] == occasion]
    if category != 'all':
        filtered = [p for p in filtered if p['category'] == category]
    if section != 'all':
        filtered = [p for p in filtered if p['section'] == section]

    return jsonify(filtered)

@app.route('/')
def home():
    # Render the HTML template below
    with open("index.html", "r", encoding="utf-8") as f:
        return render_template_string(f.read())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
