from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get DB config from environment variables
SERVICE_NAME = os.getenv("SERVICE_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

@app.route('/', methods=['GET'])
def home():
    return f"Hello from {SERVICE_NAME} service"

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json  # Expecting JSON input with 'username' and 'password'

    # Get username and password from request
    username = data.get('username')
    password = data.get('password')
    role     = data.get('role')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    try:
        # Insert new user into the database
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO accounts (username, password, role, last_login, last_logout)
        VALUES (%s, %s, %s, NULL, NULL)  RETURNING id;
        """
        cursor.execute(insert_query, (username, hashed_password, role))
        user_id = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "User created successfully", "user_id": user_id}), 201

    except psycopg2.Error as e:
        # Handle database errors
        return jsonify({"error": str(e)}), 500

@app.route('/change_password', methods=['PUT'])
def change_password():
    data = request.json  # Expecting JSON input with 'username', 'old_password', and 'new_password'

    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not username or not old_password or not new_password:
        return jsonify({"error": "Username, old password, and new password are required"}), 400

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the user's current password and role from the database
        cursor.execute("SELECT password, role FROM accounts WHERE username = %s", (username,))
        user_data = cursor.fetchone()

        if user_data is None:
            return jsonify({"error": "User not found"}), 404

        stored_password, role = user_data

        # Check if the user is an admin (admin is not allowed to change password)
        if role == 'admin':
            return jsonify({"error": "Admin is not allowed to change the password"}), 403

        # Verify the old password
        if not check_password_hash(stored_password, old_password):
            return jsonify({"error": "Old password is incorrect"}), 401

        # Hash the new password
        hashed_new_password = generate_password_hash(new_password)

        # Update the user's password in the database
        cursor.execute("UPDATE accounts SET password = %s WHERE username = %s", (hashed_new_password, username))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Password changed successfully"}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.json  # Expecting JSON input with 'username' and 'password'

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the user's password and role from the database
        cursor.execute("SELECT password, role FROM accounts WHERE username = %s", (username,))
        user_data = cursor.fetchone()

        if user_data is None:
            return jsonify({"error": "User not found"}), 404

        stored_password, role = user_data

        # Check if the user is an admin (admins are not allowed to be deleted)
        if role == 'admin':
            return jsonify({"error": "Admin is not allowed to delete their account"}), 403

        # Verify the password
        if not check_password_hash(stored_password, password):
            return jsonify({"error": "Incorrect password"}), 401

        # Delete the user from the database
        cursor.execute("DELETE FROM accounts WHERE username = %s", (username,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "User deleted successfully"}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
