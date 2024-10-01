from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime


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
def getDBConnection():
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

@app.route('/createUser', methods=['POST'])
def createUser():
    """
    Create a new user in the accounts table.

    This function handles a POST request to create a new user. It expects
    the request payload to contain 'username', 'password', and optionally 'role'.
    The username and password are required fields. If either is missing,
    it returns a 400 response with an error message.

    The function connects to the PostgreSQL database to insert the new user's
    information, including their username, password, and role. It also initializes
    the 'last_login' and 'last_logout' fields as NULL.

    Upon successful creation of the user, it returns the user's ID along with
    a success message and a 201 status code. If a database error occurs,
    it catches the error and returns a 500 response.

    Parameters:
    - The request must include a JSON body with 'username', 'password', and 'role'.

    Returns:
    - On success: a JSON response with a message and the user ID, status code 201.
    - On failure (missing fields): a JSON error message with status code 400.
    - On database error: a JSON error message with status code 500.
    """
    data = request.json

    username = data.get('username')
    password = data.get('password')
    role     = data.get('role')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        insertQuery = """
        INSERT INTO accounts (username, password, role, last_login, last_logout)
        VALUES (%s, %s, %s, NULL, NULL)  RETURNING id;
        """
        cursor.execute(insertQuery, (username, password, role))
        userId = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "User created successfully", "userId": userId}), 201

    except psycopg2.Error as e:
        # Handle database errors
        return jsonify({"error": str(e)}), 500

@app.route('/changePassword', methods=['PUT'])
def changePassword():
    """
    Change the user's password.

    This function handles a PUT request to change the user's password. It expects
    the request payload to contain 'username', 'oldPassword', and 'newPassword'.
    All three fields are required. If any of these are missing, the function returns
    a 400 response with an error message.

    Parameters:
    - The request must include a JSON body with 'username', 'oldPassword', and 'newPassword'.

    Returns:
    - On success: a JSON response with a message, status code 200.
    - On failure (missing fields): a JSON error message with status code 400.
    - On failure (user not found): a JSON error message with status code 404.
    - On failure (admin trying to change password): a JSON error message with status code 403.
    - On failure (incorrect old password): a JSON error message with status code 401.
    - On database error: a JSON error message with status code 500.
    """
    data = request.json

    username = data.get('username')
    oldPassword = data.get('oldPassword')
    newPassword = data.get('newPassword')

    if not username or not oldPassword or not newPassword:
        return jsonify({"error": "Username, old password, and new password are required"}), 400

    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        # Fetch the user's current password and role from the database
        cursor.execute("SELECT password, role FROM accounts WHERE username = %s", (username,))
        userData = cursor.fetchone()

        if userData is None:
            return jsonify({"error": "User not found"}), 404

        storedPassword, role = userData

        # Check if the user is an admin (admin is not allowed to change password)
        if role == 'admin':
            return jsonify({"error": "Admin is not allowed to change the password"}), 403

        # Verify the old password
        if storedPassword != oldPassword:
            return jsonify({"error": "Old password is incorrect"}), 401

        # Update the user's password in the database
        cursor.execute("UPDATE accounts SET password = %s WHERE username = %s", (newPassword, username))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Password changed successfully"}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deleteUser', methods=['DELETE'])
def deleteUser():
    """
    Delete a user from the accounts table.

    This function handles a DELETE request to delete a user. It expects
    the request payload to contain 'username' and 'password'. Both fields
    are required. If either is missing, the function returns a 400 response
    with an error message.

    Parameters:
    - The request must include a JSON body with 'username' and 'password'.

    Returns:
    - On success: a JSON response with a message, status code 200.
    - On failure (missing fields): a JSON error message with status code 400.
    - On failure (user not found): a JSON error message with status code 404.
    - On failure (admin account cannot be deleted): a JSON error message with status code 403.
    - On failure (incorrect password): a JSON error message with status code 401.
    - On database error: a JSON error message with status code 500.
    """
    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        # Fetch the user's password and role from the database
        cursor.execute("SELECT password, role FROM accounts WHERE username = %s", (username,))
        userData = cursor.fetchone()

        if userData is None:
            return jsonify({"error": "User not found"}), 404

        storedPassword, role = userData

        # Check if the user is an admin (admins are not allowed to be deleted)
        if role == 'admin':
            return jsonify({"error": "Admin is not allowed to delete their account"}), 403

        # Verify the password
        if storedPassword != password:
            return jsonify({"error": "Incorrect password"}), 401

        # Delete the user from the database
        cursor.execute("DELETE FROM accounts WHERE username = %s", (username,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "User deleted successfully"}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getLastLogin/<username>', methods=['GET'])
def getLastLogin(username):
    """
    Retrieve the last login time of a user.

    This function handles a GET request to fetch the last login time for a user
    based on their username. The username is passed as a path parameter.
    If the username is not found in the database, it returns a 404 response.

    Parameters:
    - username (string): The username passed as a URL parameter.

    Returns:
    - On success: a JSON response with the last login timestamp, status code 200.
    - On failure (user not found): a JSON error message with status code 404.
    - On database error: a JSON error message with status code 500.
    """
    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        # Fetch the last login time from the database
        cursor.execute("SELECT last_login FROM accounts WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({"error": "User not found"}), 404

        lastLogin = result[0]

        cursor.close()
        conn.close()

        return jsonify({"last_login": lastLogin}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getLastLogout/<username>', methods=['GET'])
def getLastLogout(username):
    """
    Retrieve the last logout time of a user.

    This function handles a GET request to fetch the last logout time for a user
    based on their username. The username is passed as a path parameter.
    If the username is not found in the database, it returns a 404 response.

    Parameters:
    - username (string): The username passed as a URL parameter.

    Returns:
    - On success: a JSON response with the username and the last logout timestamp, status code 200.
    - On failure (user not found): a JSON error message with status code 404.
    - On database error: a JSON error message with status code 500.
    """
    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        # Fetch last logout time
        cursor.execute("SELECT last_logout FROM accounts WHERE username = %s", (username,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result is None:
            return jsonify({"error": "User not found"}), 404

        lastLogout = result[0]

        return jsonify({"username": username, "last_logout": lastLogout}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verifyLogin', methods=['POST'])
def verifyLogin():
    """
    Verify user login credentials.

    This function handles a POST request to verify a user's login credentials.
    It expects the request payload to contain 'username' and 'password'.
    Both fields are required. If either is missing, it returns a 400 response
    with an error message.

    Parameters:
    - The request must include a JSON body with 'username' and 'password'.

    Returns:
    - On success: a JSON response with a success message, status code 200.
    - On failure (missing fields): a JSON error message with status code 400.
    - On failure (user not found): a JSON error message with status code 404.
    - On failure (incorrect password): a JSON error message with status code 401.
    - On database error: a JSON error message with status code 500.
    """
    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM accounts WHERE username = %s", (username,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result is None:
            return jsonify({"error": "User not found"}), 404

        storedPassword = result[0]

        # Check if the provided password matches the one in the database
        if storedPassword != password:
            return jsonify({"error": "Incorrect password"}), 401
        else:
            return jsonify({"message": "Login successful"}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/updateLastLogin', methods=['PUT'])
def updateLastLogin():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        lastLoginTime = datetime.now()

        # Update the last_login field in the database for the given username
        update_query = """
        UPDATE accounts
        SET last_login = %s
        WHERE username = %s;
        """
        cursor.execute(update_query, (lastLoginTime, username))

        # Commit the changes
        conn.commit()

        cursor.close()
        conn.close()

        # Check if any row was updated
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "Last login updated successfully", "last_login": lastLoginTime}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/updateLastLogout', methods=['PUT'])
def updateLastLogout():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        conn = getDBConnection()
        cursor = conn.cursor()

        lastLogoutTime = datetime.now()

        # Update the last_logout field in the database for the given username
        update_query = """
        UPDATE accounts
        SET last_logout = %s
        WHERE username = %s;
        """
        cursor.execute(update_query, (lastLogoutTime, username))

        # Commit the changes
        conn.commit()

        # Check if any row was updated
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return jsonify({"message": "Last logout updated successfully", "last_logout": lastLogoutTime}), 200

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
