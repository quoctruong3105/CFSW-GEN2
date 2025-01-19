import os
import pika
import json
from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
EVENT_BUS_HOST = os.getenv("EVENT_BUS_HOST")

def getDBconnection():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    return conn

@app.route("/", methods=["GET"])
def home():
    return f"Hello from {SERVICE_NAME} service"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route("/setupPayment", methods=["POST"])
def setupPayment():
    data = request.json
    try:
        event_connection = pika.BlockingConnection(pika.ConnectionParameters(host=EVENT_BUS_HOST))
        channel = event_connection.channel()
        channel.exchange_declare(exchange='order', exchange_type='fanout')
        channel.basic_publish(
            exchange='order',
            routing_key='',
            body=json.dumps(data)
        )
        event_connection.close()
        return jsonify({"status": "success", "message": "Payment setup event sent"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
