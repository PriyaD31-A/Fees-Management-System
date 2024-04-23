from flask import Flask, render_template, request, redirect, url_for,session
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mysql@123'
app.config['MYSQL_DB'] = 'air_ticket_reservation'
app.secret_key = 'a1'

mysql = MySQL(app)

# Home route - View available flights
@app.route('/home')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM flights WHERE available_seats > 0")
    flights = cursor.fetchall()
    cursor.close()
    return render_template('index.html', flights=flights)

# Reserve route - Make a reservation
@app.route('/reserve/<int:flight_id>', methods=['GET', 'POST'])
def reserve(flight_id):
    if request.method == 'POST':
        passenger_name = request.form['passenger_name']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO reservations (flight_id, passenger_name) VALUES (%s, %s)", (flight_id, passenger_name))
        cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id = %s", (flight_id,))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('home'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM flights WHERE id = %s", (flight_id,))
    flight = cursor.fetchone()
    cursor.close()

    return render_template('reserve.html', flight=flight)

# Reservations route - View all reservations
@app.route('/reservations')
def reservations():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT r.id, f.flight_number, f.departure, f.destination, r.passenger_name FROM reservations r JOIN flights f ON r.flight_id = f.id")
    reservations_data = cursor.fetchall()
    cursor.close()
    return render_template('reservations.html', reservations_data=reservations_data)
@app.route('/add_flight', methods=['GET','POST'])
def add_flight():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        departure = request.form['departure']
        destination = request.form['destination']
        available_seats = request.form['available_seats']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO flights (flight_number, departure, destination, available_seats) VALUES (%s, %s, %s, %s)", (flight_number, departure, destination, available_seats))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))

    return  render_template('add_flights.html')    
    
        
@app.route('/delete_flight/<int:flight_id>', methods=['GET','POST'])
def delete_flight(flight_id):
    # Deleting the vehicle from the database
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM flights WHERE id = %s", (flight_id,))
    mysql.connection.commit()
    return redirect(url_for('home'))
    
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email=request.form['email']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password,email) VALUES (%s, %s,%s)", (username, password,email))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')
if __name__ == '__main__':
    app.run(debug=True,port=7400)