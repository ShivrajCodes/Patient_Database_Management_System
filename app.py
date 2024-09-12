from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error
import random

app = Flask(__name__)

# Connect to MySQL database
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',           # Replace with your MySQL host
            database='health_monitor',   # Replace with your MySQL database name
            user='root',       # Replace with your MySQL username
            password='Soham@2006'    # Replace with your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Function to generate a unique 5-digit ID
def generate_unique_id(connection):
    cursor = connection.cursor()
    while True:
        person_id = '{:05d}'.format(random.randint(0, 99999))
        cursor.execute("SELECT id FROM persons WHERE id = %s", (person_id,))
        if not cursor.fetchone():
            return person_id

# Function to calculate BMI and categorize it
def calculate_bmi(weight, height):
    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        category = 'Underweight'
    elif 18.5 <= bmi < 24.9:
        category = 'Normal weight'
    elif 25 <= bmi < 29.9:
        category = 'Overweight'
    else:
        category = 'Obese'
    return bmi, category

# Function to assess oxygen saturation level
def assess_oxygen_level(oxygen_level):
    return 'Healthy' if oxygen_level >= 95 else 'Unhealthy'

# Route to display the form for adding a new person
@app.route('/add', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        age = int(request.form['age'])
        blood_group = request.form['blood_group']
        oxygen_saturation = float(request.form['oxygen_saturation'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])

        bmi, bmi_category = calculate_bmi(weight, height)
        oxygen_status = assess_oxygen_level(oxygen_saturation)

        connection = connect_to_db()
        if connection:
            person_id = generate_unique_id(connection)
            person_data = (person_id, name, address, phone_number, age, blood_group, oxygen_saturation, height, weight, bmi, bmi_category, oxygen_status)
            insert_person_data(connection, person_data)
            connection.close()
            return redirect(url_for('show_id', person_id=person_id))

    return render_template('add_person.html')

# Function to insert person data into the database
def insert_person_data(connection, person_data):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO persons (id, name, address, phone_number, age, blood_group, oxygen_saturation, height, weight, bmi, bmi_category, oxygen_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, person_data)
        connection.commit()
    except Error as e:
        print(f"Error while inserting data into MySQL: {e}")

# Route to display the record by ID
@app.route('/show/<person_id>')
def show_id(person_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        select_query = "SELECT * FROM persons WHERE id = %s"
        cursor.execute(select_query, (person_id,))
        record = cursor.fetchone()
        connection.close()

        if record:
            return render_template('show_record.html', record=record)
        else:
            return "Record not found."

# Route to display the form for searching by ID
@app.route('/display', methods=['GET', 'POST'])
def display_form():
    if request.method == 'POST':
        person_id = request.form['person_id']
        return redirect(url_for('show_id', person_id=person_id))
    return render_template('display_form.html')

# Route to display the main menu
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
