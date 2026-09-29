import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
CORS(app)

# Fetch database credentials from environment variables
def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
    )

# Serve Frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

# API Endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    max_price = request.args.get('max_price', 50000)
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM products WHERE price_inr <= %s"
        params = [max_price]
        
        if category and category != 'all':
            query += " AND category = %s"
            params.append(category)
            
        cursor.execute(query, params)
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier')
    password = data.get('password')

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s OR phone_number = %s", (identifier, identifier))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            return jsonify({'status': 'success', 'user': {'id': user['id'], 'name': user['full_name']}})
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
