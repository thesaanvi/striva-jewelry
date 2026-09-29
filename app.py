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
        
        # AUTO-SEED FIX: If MySQL returned 0 products, seed DEMI_FINE_PRODUCTS into MySQL right now!
        if not products and not gender and not occasion and not sub_category and not tag:
            cursor.executemany("""
                INSERT INTO products (name, gender, occasion, sub_category, price_inr, metal, description, image_url, tag, is_customizable) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, DEMI_FINE_PRODUCTS)
            conn.commit()
            
            # Re-fetch after inserting
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
