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
                "cost": (record["cost"]),
                "available_quantity": "N/A",
            }
            toppingList.append(toppingData)

    cursor.close()
    conn.close()

    return jsonify(toppingList)


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


def checkAvailableQuantity(drinkName):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # SQL query to get the comparison
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

        # Convert to integer portion
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

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Get the required quantities of each material for the specified drink and size
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

        # Execute the query with the given size and drink name
        cursor.execute(query, (size, size, drink))
        materials = cursor.fetchall()

        # Loop through each material and update the quantity
        for material in materials:
            material_id = material["material_id"]
            current_quantity = material["current_quantity"]
            required_quantity = material["required_quantity"]

            if required_quantity is None or required_quantity <= 0:
                continue  # Skip if no quantity is required for this size

            new_quantity = current_quantity - (required_quantity * sold_unit)

            # Update the material quantity in the database
            update_query = """
            UPDATE Material
            SET quantity = %s
            WHERE material_id = %s;
            """
            cursor.execute(update_query, (new_quantity, material_id))

        # Commit the changes
        conn.commit()

        return jsonify({"message": "Material quantities updated successfully"}), 200

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({"error": f"An error occurred: {e}"}), 500

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
