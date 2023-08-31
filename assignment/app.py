from flask import Flask, request, jsonify, render_template
import mysql.connector
import re
from enum import Enum
import datetime

app = Flask(__name__)

app.config["MYSQL_HOST"] = "assignment.c6ryspnh1guy.us-east-1.rds.amazonaws.com"
app.config["MYSQL_USER"] = "admin"
app.config["MYSQL_PASSWORD"] = "admin123"
app.config["MYSQL_DB"] = "ecommerce_db"

mysql_conn = mysql.connector.connect(
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_PASSWORD"],
    database=app.config["MYSQL_DB"],
)


class OrderStatus(Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    DELIVERED = "Delivered"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create-customer", methods=["POST"])
def create_customer():
    data = request.get_json()

    if not all(key in data for key in ["phone_number", "name", "city"]):
        return jsonify(message="Missing fields"), 400

    try:
        phone_number = data["phone_number"]
        name = data["name"]
        city = data["city"]

        if has_special_characters(name) or has_special_characters(city):
            return (
                jsonify(message="Name and city should not contain special characters"),
                400,
            )

        if not is_valid_phone_number(phone_number):
            return jsonify(message="Please provide a valid 10-digit phone number"), 400

        if len(data["name"]) > 90:
            return jsonify(message="Name is too long"), 400
        if len(data["city"]) > 90:
            return jsonify(message="City name is too long"), 400

        cursor = mysql_conn.cursor()

        query_check = "SELECT * FROM customers WHERE phone_number = %s"
        cursor.execute(query_check, (phone_number,))
        existing_customer = cursor.fetchone()

        if existing_customer:
            return (
                jsonify(message="The customer with this phone number already exists"),
                409,
            )

        query_insert = (
            "INSERT INTO customers (phone_number, name, city) VALUES (%s, %s, %s)"
        )
        cursor.execute(query_insert, (phone_number, data["name"], data["city"]))

        mysql_conn.commit()
        cursor.close()
        return jsonify(message="Customer created successfully"), 201
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        return jsonify(message="Error creating customer"), 500


@app.route("/create-order", methods=["POST"])
def create_order():
    data = request.get_json()

    if not all(key in data for key in ["item_name", "customer_phone"]):
        return jsonify(message="Missing fields"), 400

    cursor = mysql_conn.cursor()
    try:
        customer_query = "SELECT id FROM customers WHERE phone_number = %s"
        cursor.execute(customer_query, (data["customer_phone"],))
        customer = cursor.fetchone()

        if not customer:
            return jsonify(message="Customer not found"), 404

        insert_order_query = "INSERT INTO orders (item_name, status) VALUES (%s, %s)"
        cursor.execute(
            insert_order_query, (data["item_name"], OrderStatus.PENDING.value)
        )
        mysql_conn.commit()

        order_id = cursor.lastrowid

        insert_ref_query = (
            "INSERT INTO customer_order_ref (customer_id, order_id) VALUES (%s, %s)"
        )
        cursor.execute(insert_ref_query, (customer[0], order_id))
        mysql_conn.commit()

        cursor.close()
        return jsonify(message="Order created successfully"), 201
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        cursor.close()
        return jsonify(message="Error creating order"), 500


@app.route("/update-order-status", methods=["PATCH"])
def update_order_status():
    data = request.get_json()

    if not all(key in data for key in ["order_id", "new_status"]):
        return jsonify(message="Missing fields"), 400

    valid_statuses = [status.value for status in OrderStatus]
    
    if data['new_status'] not in valid_statuses:
        return jsonify(message='Invalid new_status value'), 400

    cursor = mysql_conn.cursor()
    try:
        order_id = data["order_id"]
        check_order_query = "SELECT * FROM orders WHERE id = %s"
        cursor.execute(check_order_query, (order_id,))
        existing_order = cursor.fetchone()

        if not existing_order:
            return jsonify(message="Order not found"), 404

        update_query = "UPDATE orders SET status = %s, updated_at = %s WHERE id = %s"
        cursor.execute(
            update_query,
            (data["new_status"], datetime.datetime.now(), data["order_id"]),
        )
        mysql_conn.commit()
        cursor.close()
        return jsonify(message="Order status updated successfully"), 200
    except mysql.connector.Error as e:
        mysql_conn.rollback()
        cursor.close()
        return jsonify(message="Error updating order status"), 500


@app.route("/fetch-orders-by-city", methods=["GET"])
def fetch_orders_by_city():
    city = request.args.get("city")

    if not city:
        return jsonify(message="City parameter missing"), 400

    cursor = mysql_conn.cursor(dictionary=True)
    try:

        check_city_query = "SELECT COUNT(*) AS count FROM customers WHERE city = %s"
        cursor.execute(check_city_query, (city,))
        city_count = cursor.fetchone()["count"]

        if city_count == 0:
            return jsonify(message="City not found"), 404

        query = """
            SELECT o.id AS order_id, c.id AS customer_id, c.name AS customer_name,
                   o.status AS order_status, o.item_name
            FROM orders o
            JOIN customer_order_ref cr ON o.id = cr.order_id
            JOIN customers c ON cr.customer_id = c.id
            WHERE c.city = %s
            ORDER BY c.name
        """
        cursor.execute(query, (city,))
        orders = cursor.fetchall()
        cursor.close()

        if not orders:
            return jsonify(message="No orders found in the city"), 404

        return jsonify(orders), 200
    except mysql.connector.Error as e:
        cursor.close()
        return jsonify(message="Error fetching orders by city"), 500


def has_special_characters(input_string):
    return bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', input_string))


def is_valid_phone_number(phone_number):
    return len(phone_number) == 10 and phone_number.isdigit()


if __name__ == "__main__":
    app.run(debug=True)
