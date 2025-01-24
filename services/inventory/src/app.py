from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv
import pika
from psycopg2.extras import RealDictCursor
import json
import threading
import requests
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

@app.route("/getListCake", methods=["GET"])
def getListCake():
    conn = getDBconnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM CAKE;")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(records)


@app.route("/updateCakeQuantity", methods=["POST"])
def updateCakeQuantity():
    try:
        data = request.json
        cake = data.get("cake")
        soldUnit = data.get("sold_unit")
        if not cake or soldUnit is None:
            return (
                jsonify(
                    {"error": "Invalid input. Both cake and sold_unit are required."}
                ),
                400,
            )
        conn = getDBconnection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT quantity FROM CAKE WHERE cake = %s", (cake,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Cake not found"}), 404
        currentQuantity = result["quantity"]
        newQuantity = currentQuantity - soldUnit
        if newQuantity < 0:
            return jsonify({"error": "Not enough quantity available"}), 400
        cursor.execute(
            "UPDATE CAKE SET quantity = %s WHERE cake = %s", (newQuantity, cake)
        )
        conn.commit()
        return jsonify({"message": "Cake quantities updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/getListTopping", methods=["GET"])
def getListTopping():
    conn = getDBconnection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT topping, cost FROM TOPPING;")
    records = cursor.fetchall()

    toppingList = []

    for record in records:
        topping = record["topping"]
        is_available, available_quantity = checkToppingState(topping)

        if is_available:
            toppingData = {
                "topping": topping,
                "cost": (record["cost"]),
                "available_quantity": available_quantity,
            }
            toppingList.append(toppingData)
        else:
            toppingData = {
                "topping": topping,
                "cost": (record["cost"]),
                "available_quantity": "N/A",
            }
            toppingList.append(toppingData)

    cursor.close()
    conn.close()

    return jsonify(toppingList)


def checkToppingState(topping):
    try:
        conn = getDBconnection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            "SELECT quantity, quantity_per_drink FROM TOPPING WHERE topping = %s",
            (topping,),
        )
        result = cursor.fetchone()

        if not result:
            return {"error": "Topping not found"}

        quantity = result["quantity"]
        quantityPerDrink = result["quantity_per_drink"]

        availableQuantity = float(quantity / quantityPerDrink)
        if availableQuantity < 1:
            availableQuantity = 0
            return False, availableQuantity
        else:
            return True, int(availableQuantity)

    except Exception as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


@app.route("/updateToppingQuantity", methods=["POST"])
def updateToppingQuantity():
    try:
        data = request.json
        topping = data.get("topping")
        soldUnit = data.get("sold_unit")

        if not topping or soldUnit is None:
            return (
                jsonify(
                    {"error": "Invalid input. Both topping and sold_unit are required."}
                ),
                400,
            )
        conn = getDBconnection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT quantity, quantity_per_drink FROM TOPPING WHERE topping = %s",
            (topping,),
        )
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Topping not found"}), 404
        quantity = result["quantity"]
        quantityPerDrink = result["quantity_per_drink"]
        newQuantity = quantity - (quantityPerDrink * soldUnit)
        if newQuantity < 0:
            return jsonify({"error": "Not enough quantity available"}), 400
        cursor.execute(
            "UPDATE TOPPING SET quantity = %s WHERE topping = %s",
            (newQuantity, topping),
        )
        conn.commit()
        return jsonify({"message": "Topping quantities updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


def checkAvailableQuantity(drinkName):
    conn = getDBconnection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT
        m.material_id,
        m.material,
        dm.m_quantity,
        dm.l_quantity,
        m.quantity,
        CASE
            WHEN dm.m_quantity > 0 THEN m.quantity / dm.m_quantity
            ELSE NULL
        END AS available_quantity_m,
        CASE
            WHEN dm.l_quantity > 0 THEN m.quantity / dm.l_quantity
            ELSE NULL
        END AS available_quantity_l
    FROM
        Material m
    JOIN
        Drink_Material dm ON m.material_id = dm.material_id
    JOIN
        Drink d ON dm.drink_id = d.drink_id
    WHERE
        d.drink = %s;
    """

    try:
        cursor.execute(query, (drinkName,))
        results = cursor.fetchall()

        available_quantity_m = {
            item["material"]: item["available_quantity_m"] for item in results
        }
        available_quantity_l = {
            item["material"]: item["available_quantity_l"] for item in results
        }

        available_quantity_m = {
            key: int(value) for key, value in available_quantity_m.items()
        }
        available_quantity_l = {
            key: int(value) for key, value in available_quantity_l.items()
        }

        return available_quantity_m, available_quantity_l

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

    finally:
        cursor.close()
        conn.close()


@app.route("/getListDrink", methods=["GET"])
def getListDrink():
    conn = getDBconnection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
    SELECT
        d.drink,
        d.m_cost,
        d.l_cost,
        dg.drink_group AS "group"  -- Renamed to avoid conflict with the keyword
    FROM
        Drink d
    JOIN
        Drink_Group dg ON d.drink_group_id = dg.drink_group_id;  -- Joining Drink and Drink_Group
    """
    cursor.execute(query)
    records = cursor.fetchall()

    drinkList = []

    for record in records:
        drinkName = record["drink"]

        available_quantity_m, available_quantity_l = checkAvailableQuantity(drinkName)
        drinkData = {
            "drink": drinkName,
            "m_cost": record["m_cost"],
            "l_cost": record["l_cost"],
            "group": record["group"],
            "available_quantity_m": available_quantity_m,
            "available_quantity_l": available_quantity_l,
        }

        drinkList.append(drinkData)

    cursor.close()
    conn.close()

    return jsonify(drinkList)


@app.route("/updateMaterialQuantity", methods=["POST"])
def updateMaterialQuantity():
    data = request.get_json()
    drink = data.get("drink")
    size = data.get("size")  # "m" or "l"
    sold_unit = data.get("sold_unit")

    conn = getDBconnection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = """
        SELECT
            m.material_id,
            m.quantity AS current_quantity,
            CASE
                WHEN %s = 'm' THEN dm.m_quantity
                WHEN %s = 'l' THEN dm.l_quantity
                ELSE 0
            END AS required_quantity
        FROM
            Material m
        JOIN
            Drink_Material dm ON m.material_id = dm.material_id
        JOIN
            Drink d ON dm.drink_id = d.drink_id
        WHERE
            d.drink = %s;
        """

        cursor.execute(query, (size, size, drink))
        materials = cursor.fetchall()
        for material in materials:
            material_id = material["material_id"]
            current_quantity = material["current_quantity"]
            required_quantity = material["required_quantity"]

            if required_quantity is None or required_quantity <= 0:
                continue

            new_quantity = current_quantity - (required_quantity * sold_unit)
            update_query = """
            UPDATE Material
            SET quantity = %s
            WHERE material_id = %s;
            """
            cursor.execute(update_query, (new_quantity, material_id))
        conn.commit()
        return jsonify({"message": "Material quantities updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        cursor.close()
        conn.close()

def onConfirmPayment():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(EVENT_BUS_HOST))
        channel = connection.channel()

        channel.exchange_declare(exchange='order', exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='order', queue=queue_name)

        def callback(ch, method, properties, body):
            message = json.loads(body)
            drink = message.get('drink', [])
            print(f"drink: {drink}")
            for dr in drink:
                dr_data = {
                    'drink': dr.get('name'),
                    'size': dr.get('size'),
                    'sold_unit': dr.get('quantity')
                }
                try:
                    response = requests.post("http://localhost:5000/updateMaterialQuantity", json=dr_data)
                    print(f"Update Response: {response.json()}")
                except Exception as e:
                    print(f"Error calling updateMaterialQuantity API: {str(e)}")
                topping = dr.get('topping', [])
                for tp in topping:
                    tp_data = {
                        'topping': tp.get('name'),
                        'sold_unit': tp.get('quantity')
                    }
                    try:
                        response = requests.post("http://localhost:5000/updateToppingQuantity", json=tp_data)
                    except Exception as e:
                        print(f"Error calling updateMaterialQuantity API: {str(e)}")
            cake = message.get('cake', [])
            print(f"cake: {cake}")
            for ck in cake:
                ck_data = {
                    'cake': ck.get('name'),
                    'sold_unit': ck.get('quantity')
                }
                try:
                    response = requests.post("http://localhost:5000/updateCakeQuantity", json=ck_data)
                except Exception as e:
                    print(f"Error calling updateMaterialQuantity API: {str(e)}")

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    except Exception as e:
        print(f"Error while consuming messages: {str(e)}")


threading.Thread(target=onConfirmPayment, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
