import os
import json
from decimal import Decimal

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# STRIVA - FLASK BACKEND
# ============================================================

app = Flask(__name__, static_folder="static")
CORS(app)


# ============================================================
# DATABASE SETTINGS
# ============================================================
# For local MySQL, these defaults are:
# host     = localhost
# port     = 3306
# user     = root
# password = ""
# database = striva
#
# If you use another database, set these environment variables:
# DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME
# ============================================================

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "striva")


def get_server_connection():
    """Connect to MySQL server without selecting a database."""
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS
    )


def create_database_if_needed():
    """Create the STRIVA database if it does not already exist."""
    conn = get_server_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_db():
    """Connect directly to the STRIVA database."""
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )


# ============================================================
# PRODUCT CATALOG
# ============================================================
# image_url values are real URLs, NOT Markdown links.
# ============================================================

ALL_PRODUCTS = [
    # ---------------- WOMEN / MINIMAL ----------------
    {
        "sku": "STR-W-NK-001",
        "name": "Aura Mother-of-Pearl Layered Necklace",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "necklaces",
        "price_inr": 4299,
        "metal": "18K Gold Vermeil",
        "description": "A delicate layered necklace finished with a luminous mother-of-pearl inspired pendant.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900",
        "tag": "bestseller",
        "is_customizable": True
    },
    {
        "sku": "STR-W-RG-001",
        "name": "Classic Solitaire Bezel Ring",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "rings",
        "price_inr": 2899,
        "metal": "18K Gold Vermeil",
        "description": "A refined bezel-set solitaire ring designed for understated everyday styling.",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=900",
        "tag": "favourites",
        "is_customizable": True
    },
    {
        "sku": "STR-W-RG-002",
        "name": "Celestial Moon & Star Ring Stack",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "rings",
        "price_inr": 3499,
        "metal": "18K Gold Vermeil",
        "description": "A stack of delicate celestial-inspired bands made for effortless layering.",
        "image_url": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=900",
        "tag": "trending",
        "is_customizable": True
    },
    {
        "sku": "STR-W-ER-001",
        "name": "Chunky Polished Vermeil Hoops",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "earrings",
        "price_inr": 2199,
        "metal": "18K Gold Vermeil",
        "description": "Smooth tubular hoops with a polished finish and a clean contemporary silhouette.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=900",
        "tag": "bestseller",
        "is_customizable": False
    },
    {
        "sku": "STR-W-RG-003",
        "name": "Textured Croissant Dome Ring",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "rings",
        "price_inr": 2699,
        "metal": "18K Gold Vermeil",
        "description": "A softly ridged dome ring inspired by sculptural French jewellery forms.",
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=900",
        "tag": "trending",
        "is_customizable": False
    },
    {
        "sku": "STR-W-RG-004",
        "name": "High-Polish Dome Ring",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "rings",
        "price_inr": 2499,
        "metal": "18K Gold Vermeil",
        "description": "A sleek rounded dome band with a mirror-polished finish.",
        "image_url": "https://images.unsplash.com/photo-1627293509201-cd1b3d9d3f6d?w=900",
        "tag": "favourites",
        "is_customizable": False
    },
    {
        "sku": "STR-W-ER-002",
        "name": "Pavé Hexagon Cluster Studs",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "earrings",
        "price_inr": 1899,
        "metal": "18K Gold Vermeil",
        "description": "Geometric stud earrings with a refined pavé-inspired centre.",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=900",
        "tag": "bestseller",
        "is_customizable": False
    },
    {
        "sku": "STR-W-NK-002",
        "name": "Liquid Gold Herringbone Chain",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "necklaces",
        "price_inr": 3899,
        "metal": "18K Gold Vermeil",
        "description": "A fluid herringbone-inspired chain designed to sit close to the collarbone.",
        "image_url": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=900",
        "tag": "favourites",
        "is_customizable": False
    },
    {
        "sku": "STR-W-BR-001",
        "name": "Luna Pearl Crescent Bracelet",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "bracelets",
        "price_inr": 2999,
        "metal": "18K Gold Vermeil & Pearl",
        "description": "A delicate bracelet combining luminous pearl details with a crescent-inspired charm.",
        "image_url": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=900",
        "tag": "trending",
        "is_customizable": True
    },
    {
        "sku": "STR-W-BR-002",
        "name": "Paperclip Link Charm Bracelet",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "bracelets",
        "price_inr": 3299,
        "metal": "18K Gold Vermeil",
        "description": "A modern paperclip-link bracelet finished with a small signature charm.",
        "image_url": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=900",
        "tag": "bestseller",
        "is_customizable": True
    },
    {
        "sku": "STR-W-AK-001",
        "name": "Delicate Beaded Gold Anklet",
        "gender": "women",
        "occasion": "minimal",
        "sub_category": "anklets",
        "price_inr": 1499,
        "metal": "18K Gold Vermeil",
        "description": "A fine beaded anklet with a subtle polished finish for everyday styling.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=900",
        "tag": "favourites",
        "is_customizable": False
    },

    # ---------------- WOMEN / WEDDING ----------------
    {
        "sku": "STR-W-WD-001",
        "name": "Royal Kundan Heritage Nath",
        "gender": "women",
        "occasion": "wedding",
        "sub_category": "nose-rings",
        "price_inr": 3499,
        "metal": "18K Gold Vermeil & Pearl",
        "description": "A lightweight festive nose ring with refined pearl and stone-inspired detailing.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=900",
        "tag": "festive",
        "is_customizable": False
    },
    {
        "sku": "STR-W-WD-002",
        "name": "Crescent Kundan Maang Tikka",
        "gender": "women",
        "occasion": "wedding",
        "sub_category": "maang-tikka",
        "price_inr": 3199,
        "metal": "18K Gold Vermeil",
        "description": "A lightweight crescent-inspired maang tikka for modern wedding styling.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=900",
        "tag": "trending",
        "is_customizable": False
    },
    {
        "sku": "STR-W-WD-003",
        "name": "Modern Solitaire Mangalsutra",
        "gender": "women",
        "occasion": "wedding",
        "sub_category": "mangalsutras",
        "price_inr": 6899,
        "metal": "18K Gold Vermeil",
        "description": "A contemporary mangalsutra silhouette centred around a refined solitaire-inspired pendant.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900",
        "tag": "bestseller",
        "is_customizable": True
    },
    {
        "sku": "STR-W-WD-004",
        "name": "Bridal Gold Vermeil Choker",
        "gender": "women",
        "occasion": "wedding",
        "sub_category": "necklaces",
        "price_inr": 8999,
        "metal": "18K Gold Vermeil",
        "description": "A refined bridal choker designed to pair with contemporary Indian wedding looks.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900",
        "tag": "favourites",
        "is_customizable": False
    },
    {
        "sku": "STR-W-WD-005",
        "name": "Pearl Halo Bridal Earrings",
        "gender": "women",
        "occasion": "wedding",
        "sub_category": "earrings",
        "price_inr": 7499,
        "metal": "18K Gold Vermeil & Pearl",
        "description": "Elegant drop earrings with a pearl-led bridal silhouette.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=900",
        "tag": "festive",
        "is_customizable": False
    },

    # ---------------- MEN / MINIMAL ----------------
    {
        "sku": "STR-M-RG-001",
        "name": "Homme Brushed Silver Signet Ring",
        "gender": "men",
        "occasion": "minimal",
        "sub_category": "rings",
        "price_inr": 2899,
        "metal": "925 Sterling Silver",
        "description": "A clean brushed-finish signet ring designed for understated everyday wear.",
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=900",
        "tag": "bestseller",
        "is_customizable": True
    },
    {
        "sku": "STR-M-CH-001",
        "name": "Beveled Heavy Curb Chain",
        "gender": "men",
        "occasion": "minimal",
        "sub_category": "chains",
        "price_inr": 4999,
        "metal": "925 Sterling Silver",
        "description": "A substantial curb-chain silhouette with clean beveled links.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900",
        "tag": "trending",
        "is_customizable": False
    },
    {
        "sku": "STR-M-BR-001",
        "name": "Hammered Gold Kada Cuff",
        "gender": "men",
        "occasion": "minimal",
        "sub_category": "bracelets",
        "price_inr": 4200,
        "metal": "18K Gold Vermeil",
        "description": "A sculptural kada-style cuff with subtle hammered texture.",
        "image_url": "https://images.unsplash.com/photo-1611591475179-62cd34feb0ce?w=900",
        "tag": "favourites",
        "is_customizable": True
    },
    {
        "sku": "STR-M-ER-001",
        "name": "Single Huggie Hoop",
        "gender": "men",
        "occasion": "minimal",
        "sub_category": "earrings",
        "price_inr": 1199,
        "metal": "925 Sterling Silver",
        "description": "A compact polished huggie hoop designed for a subtle everyday look.",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=900",
        "tag": "bestseller",
        "is_customizable": False
    },
    {
        "sku": "STR-M-CH-002",
        "name": "Classic Box Link Chain",
        "gender": "men",
        "occasion": "minimal",
        "sub_category": "chains",
        "price_inr": 3799,
        "metal": "925 Sterling Silver",
        "description": "A clean box-link chain with a polished contemporary finish.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900",
        "tag": "favourites",
        "is_customizable": False
    },

    # ---------------- MEN / WEDDING ----------------
    {
        "sku": "STR-M-WD-001",
        "name": "Royal Emerald Sherwani Brooch",
        "gender": "men",
        "occasion": "wedding",
        "sub_category": "brooches",
        "price_inr": 4200,
        "metal": "18K Gold Vermeil & Emerald",
        "description": "A refined statement brooch designed for sherwanis and formal weddingwear.",
        "image_url": "https://images.unsplash.com/photo-1600003014755-ba31aa59c4b6?w=900",
        "tag": "festive",
        "is_customizable": False
    },
    {
        "sku": "STR-M-WD-002",
        "name": "Groom Layered Pearl Necklace",
        "gender": "men",
        "occasion": "wedding",
        "sub_category": "necklaces",
        "price_inr": 7999,
        "metal": "18K Gold Vermeil & Pearl",
        "description": "A contemporary layered pearl necklace designed for modern groom styling.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=900",
        "tag": "trending",
        "is_customizable": False
    },
    {
        "sku": "STR-M-WD-003",
        "name": "Wedding Signet Cufflinks",
        "gender": "men",
        "occasion": "wedding",
        "sub_category": "cufflinks",
        "price_inr": 3999,
        "metal": "925 Sterling Silver",
        "description": "Minimal polished cufflinks with a strong signet-inspired face.",
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=900",
        "tag": "favourites",
        "is_customizable": True
    },

    # ---------------- COUPLE ----------------
    {
        "sku": "STR-C-RG-001",
        "name": "Eternal Couple Ring Set",
        "gender": "couple",
        "occasion": "wedding",
        "sub_category": "couple-rings",
        "price_inr": 8999,
        "metal": "18K Gold Vermeil",
        "description": "A coordinated couple ring set with clean contemporary profiles and optional engraving.",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=900",
        "tag": "bestseller",
        "is_customizable": True
    },
    {
        "sku": "STR-C-RG-002",
        "name": "Always & Forever Ring Pair",
        "gender": "couple",
        "occasion": "wedding",
        "sub_category": "couple-rings",
        "price_inr": 9499,
        "metal": "925 Sterling Silver",
        "description": "A matching pair of understated bands designed for personal engraving.",
        "image_url": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=900",
        "tag": "favourites",
        "is_customizable": True
    },
]


# ============================================================
# DATABASE TABLES + SEED
# ============================================================

def ensure_tables_and_seed():
    """Create missing tables/columns and seed the STRIVA catalog.

    IMPORTANT: Aiven already contains the database/table in many deployments.
    CREATE TABLE IF NOT EXISTS does NOT change an existing table, so this
    function also performs a small schema migration for older products tables.
    """
    conn = None
    cursor = None

    try:
        # Aiven normally already provides the database. This is kept for
        # compatibility with local MySQL setups too.
        try:
            create_database_if_needed()
        except Error as db_create_error:
            # If the database already exists but the Aiven user is not allowed
            # to CREATE DATABASE, continue and connect to the existing DB.
            print("Database creation skipped:", db_create_error)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku VARCHAR(100),
                name VARCHAR(255) NOT NULL,
                gender VARCHAR(30),
                occasion VARCHAR(30),
                sub_category VARCHAR(80),
                price_inr DECIMAL(10,2) NOT NULL DEFAULT 0,
                metal VARCHAR(150),
                description TEXT,
                image_url TEXT,
                tag VARCHAR(50),
                is_customizable BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                items_json LONGTEXT NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(50) DEFAULT 'Processing',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)

        # ------------------------------------------------------------
        # MIGRATE OLD PRODUCTS TABLE
        # ------------------------------------------------------------
        # The previous version of STRIVA may already have a products table.
        # CREATE TABLE IF NOT EXISTS will NOT add columns to that table.
        # Check every column used by the current API and add it if missing.
        required_columns = {
            "sku": "VARCHAR(100) NULL",
            "category": "VARCHAR(80) NULL",
            "gender": "VARCHAR(30) NULL",
            "occasion": "VARCHAR(30) NULL",
            "sub_category": "VARCHAR(80) NULL",
            "price_inr": "DECIMAL(10,2) NOT NULL DEFAULT 0",
            "metal": "VARCHAR(150) NULL",
            "description": "TEXT NULL",
            "image_url": "TEXT NULL",
            "tag": "VARCHAR(50) NULL",
            "is_customizable": "BOOLEAN DEFAULT TRUE",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }

        for column_name, column_definition in required_columns.items():
            cursor.execute(
                "SHOW COLUMNS FROM products LIKE %s",
                (column_name,)
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    f"ALTER TABLE products ADD COLUMN `{column_name}` {column_definition}"
                )
                print(f"Added missing products column: {column_name}")

        # Existing old rows are allowed to remain. The newly seeded STRIVA
        # products below always receive complete values.
        conn.commit()

        # ------------------------------------------------------------
        # SEED / UPDATE PRODUCTS
        # ------------------------------------------------------------
        # Do not depend on the table being empty. Match products by SKU so
        # redeploying on Render does not create duplicates.
        for p in ALL_PRODUCTS:
            cursor.execute(
                "SELECT id FROM products WHERE sku = %s LIMIT 1",
                (p["sku"],)
            )
            existing = cursor.fetchone()

            values = (
                p["name"],
                p["sub_category"],
                p["gender"],
                p["occasion"],
                p["sub_category"],
                p["price_inr"],
                p["metal"],
                p["description"],
                p["image_url"],
                p["tag"],
                p["is_customizable"],
                p["sku"],
            )

            if existing:
                cursor.execute(
                    """
                    UPDATE products SET
                        name = %s,
                        category = %s,
                        gender = %s,
                        occasion = %s,
                        sub_category = %s,
                        price_inr = %s,
                        metal = %s,
                        description = %s,
                        image_url = %s,
                        tag = %s,
                        is_customizable = %s
                    WHERE id = %s
                    """,
                    values[:-1] + (existing[0],)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO products
                    (sku, name, category, gender, occasion, sub_category, price_inr,
                     metal, description, image_url, tag, is_customizable)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        p["sku"],
                        p["name"],
                        p["sub_category"],
                        p["gender"],
                        p["occasion"],
                        p["sub_category"],
                        p["price_inr"],
                        p["metal"],
                        p["description"],
                        p["image_url"],
                        p["tag"],
                        p["is_customizable"],
                    )
                )

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"STRIVA database ready. Catalog contains {total_products} products.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("DATABASE SETUP ERROR:", e)
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================
# HELPERS
# ============================================================

def serialize_product(product):
    """Make Decimal values JSON-friendly."""
    if product and isinstance(product.get("price_inr"), Decimal):
        product["price_inr"] = float(product["price_inr"])
    return product


def api_error(message, status=500):
    return jsonify({
        "status": "error",
        "message": message
    }), status


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():
    try:
        ensure_tables_and_seed()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "STRIVA backend is running.",
            "product_count": count
        })
    except Exception as e:
        return api_error(str(e))


# ============================================================
# AUTH
# ============================================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return api_error("Name, email and password are required.", 400)

    try:
        ensure_tables_and_seed()

        conn = get_db()
        cursor = conn.cursor()

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (name, email, password_hash)
        )

        conn.commit()
        user_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        })

    except mysql.connector.IntegrityError:
        return api_error("Email address is already registered.", 400)

    except Exception as e:
        return api_error(str(e))


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return api_error("Email and password are required.", 400)

    try:
        ensure_tables_and_seed()

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "status": "success",
                "user": {
                    "id": user["id"],
                    "name": user["full_name"],
                    "email": user["email"]
                }
            })

        return api_error("Invalid email or password.", 401)

    except Exception as e:
        return api_error(str(e))


# ============================================================
# PRODUCTS
# ============================================================

@app.route("/api/products", methods=["GET"])
def get_products():
    gender = request.args.get("gender", "all")
    occasion = request.args.get("occasion", "all")
    sub_category = request.args.get("sub_category", "all")
    tag = request.args.get("tag", "all")
    max_price = request.args.get("max_price")

    try:
        ensure_tables_and_seed()

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                id,
                sku,
                name,
                gender,
                occasion,
                sub_category,
                price_inr,
                metal,
                description,
                image_url,
                tag,
                is_customizable
            FROM products
            WHERE 1=1
        """

        params = []

        if gender and gender != "all":
            query += " AND gender = %s"
            params.append(gender)

        if occasion and occasion != "all":
            query += " AND occasion = %s"
            params.append(occasion)

        if sub_category and sub_category != "all":
            query += " AND sub_category = %s"
            params.append(sub_category)

        if tag and tag != "all":
            query += " AND tag = %s"
            params.append(tag)

        if max_price:
            try:
                max_price_value = float(max_price)
                query += " AND price_inr <= %s"
                params.append(max_price_value)
            except ValueError:
                pass

        query += " ORDER BY id ASC"

        cursor.execute(query, params)
        products = cursor.fetchall()

        cursor.close()
        conn.close()

        products = [serialize_product(p) for p in products]

        return jsonify({
            "status": "success",
            "count": len(products),
            "products": products
        })

    except Exception as e:
        print("PRODUCT API ERROR:", e)
        return api_error(str(e))


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    try:
        ensure_tables_and_seed()

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                sku,
                name,
                gender,
                occasion,
                sub_category,
                price_inr,
                metal,
                description,
                image_url,
                tag,
                is_customizable
            FROM products
            WHERE id = %s
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        cursor.close()
        conn.close()

        if not product:
            return api_error("Product not found.", 404)

        return jsonify({
            "status": "success",
            "product": serialize_product(product)
        })

    except Exception as e:
        return api_error(str(e))


# ============================================================
# ORDERS
# ============================================================

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    items = data.get("items", [])
    total_amount = data.get("total_amount", 0)

    if not user_id or not items:
        return api_error("User and order items are required.", 400)

    try:
        ensure_tables_and_seed()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO orders
            (user_id, items_json, total_amount)
            VALUES (%s, %s, %s)
            """,
            (
                user_id,
                json.dumps(items),
                total_amount
            )
        )

        conn.commit()
        order_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "order_id": order_id
        })

    except Exception as e:
        return api_error(str(e))


@app.route("/api/orders/<int:user_id>", methods=["GET"])
def get_orders(user_id):
    try:
        ensure_tables_and_seed()

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        for order in orders:
            if isinstance(order.get("total_amount"), Decimal):
                order["total_amount"] = float(order["total_amount"])

        return jsonify({
            "status": "success",
            "orders": orders
        })

    except Exception as e:
        return api_error(str(e))


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("STRIVA backend starting...")
    print(f"Database: {DB_NAME}")
    print(f"Server: http://localhost:5000")
    print("=" * 55)

    try:
        ensure_tables_and_seed()
        app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "5000")),
            debug=True
        )
    except Exception as e:
        print("\nSTRIVA COULD NOT START:")
        print(e)
        print("\nCheck your MySQL server and database credentials.")
