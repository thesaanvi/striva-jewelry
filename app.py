import os
import pymysql
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Load local environment variables from .env file if running locally
load_dotenv()

app = Flask(__name__)

# Database connection details from environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = int(os.environ.get('DB_PORT', 3306))


def get_db_connection():
    """
    Establishes and returns a MySQL database connection.
    Configured with SSL required for cloud hosting platforms like Aiven.
    """
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        ssl={'ssl': {}},  # Enforces SSL mode required by Aiven
        connect_timeout=10
    )


@app.route('/')
def home():
    """Health check route to verify server uptime."""
    return jsonify({"status": "online", "message": "Flask server running on Render"}), 200


@app.route('/db-test', methods=['GET'])
def db_test():
    """Test endpoint to verify database connectivity."""
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW() AS current_time;")
            result = cursor.fetchone()
        return jsonify({
            "status": "success",
            "message": "Successfully connected to Aiven MySQL!",
            "database_time": str(result['current_time'])
        }), 200

    except pymysql.MySQLError as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Database connection failed",
            "details": str(e)
        }), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected server error occurred",
            "details": str(e)
        }), 500

    finally:
        if connection:
            connection.close()


@app.errorhandler(500)
def handle_internal_server_error(e):
    """Global handler for 500 exceptions."""
    return jsonify({
        "status": "error",
        "message": "Internal Server Error",
        "details": str(e)
    }), 500


if __name__ == '__main__':
    # Local development server execution
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
