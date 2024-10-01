from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv
import os

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
