from flask import Flask, jsonify, request
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
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
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    return conn


@app.route("/", methods=["GET"])
def home():
    return f"Hello from {SERVICE_NAME} service"


@app.route("/getListCake", methods=["GET"])
def getListCake():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM CAKE;")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(records), 200


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

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Fetch the current quantity of the specified cake
        cursor.execute("SELECT quantity FROM CAKE WHERE cake = %s", (cake,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Cake not found"}), 404

        currentQuantity = result["quantity"]
        newQuantity = currentQuantity - soldUnit

        if newQuantity < 0:
            return jsonify({"error": "Not enough quantity available"}), 400

        # Update the quantity in the database
        cursor.execute(
            "UPDATE CAKE SET quantity = %s WHERE cake = %s", (newQuantity, cake)
        )
        conn.commit()
        return (
            jsonify(
                {"message": "Quantity updated successfully", "newQuantity": newQuantity}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/getListTopping", methods=["GET"])
def getListTopping():
    conn = get_db_connection()
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
                "cost": (record["cost"]),  # Convert to string for JSON serialization
                "available_quantity": available_quantity,  # Convert to string to maintain precision
            }
            toppingList.append(toppingData)
        else:
            toppingData = {
                "topping": topping,
                "cost": (record["cost"]) * 1000,
                "available_quantity": "N/A",
            }
            toppingList.append(toppingData)

    cursor.close()
    conn.close()

    return jsonify(toppingList), 200


def checkToppingState(topping):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Fetch the quantity and quantity_per_drink for the specified topping
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

        conn = get_db_connection()
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

        # Calculate the new quantity based on the formula
        newQuantity = quantity - (quantityPerDrink * soldUnit)

        # Ensure that the new quantity does not go below zero
        if newQuantity < 0:
            return jsonify({"error": "Not enough quantity available"}), 400

        cursor.execute(
            "UPDATE TOPPING SET quantity = %s WHERE topping = %s",
            (newQuantity, topping),
        )
        conn.commit()

        return (
            jsonify(
                {
                    "message": "Quantity updated successfully",
                    "topping": topping,
                    "new_quantity": newQuantity,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


def checkDrinkState(drinkName):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # SQL query to get the comparison
    query = """
    SELECT
        dm.drink_id,
        dm.material_id,
        dm.m_quantity,
        dm.l_quantity,
        m.quantity AS material_quantity,
        CASE
            WHEN m.quantity > 0 THEN dm.m_quantity::decimal / m.quantity
            ELSE 0
        END AS available_quantity_m,
        CASE
            WHEN m.quantity > 0 THEN dm.l_quantity::decimal / m.quantity
            ELSE 0
        END AS available_quantity_l
    FROM
        Drink_Material dm
    JOIN
        Material m ON dm.material_id = m.material_id
    JOIN
        Drink d ON dm.drink_id = d.drink_id
    WHERE
        d.drink = %s;
    """

    try:
        cursor.execute(query, (drinkName,))
        results = cursor.fetchall()

        # Print or process the results
        for row in results:
            available_quantity_m = row["available_quantity_m"]
            available_quantity_l = row["available_quantity_l"]

            return available_quantity_m, available_quantity_l

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


@app.route("/getListDrink", methods=["GET"])
def getListDrink():
    conn = get_db_connection()
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
    # Fetching all drinks
    cursor.execute(query)
    records = cursor.fetchall()

    drinkList = []

    for record in records:
        drinkName = record["drink"]

        # Check availability for medium and large drinks
        available_quantity_m, available_quantity_l = checkDrinkState(drinkName)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
