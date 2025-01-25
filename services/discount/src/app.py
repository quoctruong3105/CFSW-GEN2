from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv
import pika
import requests
import json
import threading
import os

load_dotenv()

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
EVENT_BUS_HOST = os.getenv("EVENT_BUS_HOST")

discount_events = [] # TBD

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

@app.route('/applyDiscount', methods=['POST'])
def applyDiscount(): #TDB
    global discount_events
    if not discount_events:
        return request.data, 200

def onSetupPayment():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(EVENT_BUS_HOST))
        order_channel = connection.channel()
        scanned_channel = connection.channel()

        order_channel.exchange_declare(exchange='order', exchange_type='fanout')
        scanned_channel.exchange_declare(exchange='scanned', exchange_type='fanout')

        result = order_channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        order_channel.queue_bind(exchange='order', queue=queue_name)

        def callback(ch, method, properties, body):
            message = json.loads(body)
            print(message)
            response = requests.post("http://localhost:5000/applyDiscount", json=message)
            scanned_channel.basic_publish(
                exchange='scanned',
                routing_key='',
                body=json.dumps(response.json())
            )

        order_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        order_channel.start_consuming()

    except Exception as e:
        print(f"Error while consuming messages: {str(e)}")

threading.Thread(target=onSetupPayment, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
