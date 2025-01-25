import os
import pika
import json
import requests
from flask import Flask, jsonify, request
import psycopg2
import threading
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

scanned_order = {}

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

def totalCost():
    data = request.json
    drink = data.get('drink', '')
    total = 0
    if drink:
        for dr in drink:
            total += dr.get('cost')
            topping = dr.get('topping', '')
            if topping:
                for tp in topping:
                    total += tp.get('cost')
    cake = data.get('cake', '')
    if cake:
        for ck in cake:
            total += ck.get('cost')
    discount = data.get('discount', '')
    if discount:
        pass # TBD
    return totalCost

@app.route("/exportBill", methods=['POST'])
def exportBill(): # TBD
    """Ensure the response is a proper JSON serializable dictionary."""
    return jsonify({"message": "Bill has been exported"}), 200

@app.route("/setupPayment", methods=["POST"])
def setupPayment():
    data = request.json
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(EVENT_BUS_HOST))
        channel = connection.channel()
        channel.exchange_declare(exchange='order', exchange_type='fanout')
        channel.basic_publish(
            exchange='order',
            routing_key='',
            body=json.dumps(data)
        )
        return jsonify({"status": "success", "message": "Payment setup event sent"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def onConfirmPayment():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(EVENT_BUS_HOST))
        channel = connection.channel()
        channel.exchange_declare(exchange='payment', exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='payment', queue=queue_name)

        def callback(ch, method, properties, body):
            # message = json.loads(body)
            global scanned_order
            response = requests.post("http://localhost:5000/exportBill", json=scanned_order)
            print(response.text)

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    except Exception as e:
        print(f"onConfirmPayment, Error while consuming messages: {str(e)}")


def onApplyDiscount():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(EVENT_BUS_HOST))
        channel = connection.channel()
        channel.exchange_declare(exchange='scanned', exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='scanned', queue=queue_name)

        def callback(ch, method, properties, body):
            message = json.loads(body)
            global scanned_order
            scanned_order = message

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    except Exception as e:
        print(f"onApplyDiscount, Error while consuming messages: {str(e)}")


threading.Thread(target=onApplyDiscount, daemon=True).start()
threading.Thread(target=onConfirmPayment, daemon=True).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
