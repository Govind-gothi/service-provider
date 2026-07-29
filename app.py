from flask import Flask, render_template, request, url_for, redirect, flash, session
from math import radians, sin, cos, sqrt, atan2
import mysql.connector
import re
from datetime import datetime, time, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'service-provider-marketplace-secret-key'

# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "port": int(os.getenv("DB_PORT")),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "database": os.getenv("DB_NAME")
# }

# def get_db():
#     print("DB_CONFIG =", DB_CONFIG)
#     print("DB_HOST =", os.getenv("DB_HOST"))
#     print("DB_PORT =", os.getenv("DB_PORT"))
#     print("DB_USER =", os.getenv("DB_USER"))
#     print("DB_NAME =", os.getenv("DB_NAME"))

#     return mysql.connector.connect(**DB_CONFIG)



DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "user": "root",
    "password": "54321",
    "database": "service_booking_db",
}
def get_db():
    return mysql.connector.connect(**DB_CONFIG)



def td_to_time(td):
    if isinstance(td, time):
        return td
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    h %= 24
    return time(h, m)


def time_overlap(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)


def format_time_value(value):
    if value is None:
        return ""
    if isinstance(value, timedelta):
        return td_to_time(value).strftime("%H:%M")
    if isinstance(value, time):
        return value.strftime("%H:%M")
    return str(value)[:5]


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "error")
                if role == "provider":
                    return redirect(url_for("service_provider_login"))
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("You do not have access to that page.", "error")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def get_provider_by_id(provider_id):
    mydb = get_db()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM service_provider WHERE ProviderID = %s", (provider_id,))
    provider = mycursor.fetchone()
    mycursor.close()
    mydb.close()
    return provider


def get_customer_by_id(customer_id):
    mydb = get_db()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM customer WHERE CustomerID = %s", (customer_id,))
    customer = mycursor.fetchone()
    mycursor.close()
    mydb.close()
    return customer


def slot_is_available(provider_id, booking_date, start_time, end_time, exclude_booking_id=None):
    mydb = get_db()
    mycursor = mydb.cursor()
    query = """
        SELECT Booking_Date, Start_Time, End_Time FROM bookings
        WHERE ProviderID = %s AND Status NOT IN ('Rejected', 'Completed')
    """
    params = [provider_id]
    if exclude_booking_id:
        query += " AND BookingID != %s"
        params.append(exclude_booking_id)
    mycursor.execute(query, tuple(params))
    rows = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    form_start = datetime.strptime(start_time, "%H:%M").time() if isinstance(start_time, str) else start_time
    form_end = datetime.strptime(end_time, "%H:%M").time() if isinstance(end_time, str) else end_time

    for entry_date, start_td, end_td in rows:
        if entry_date != booking_date:
            continue
        prov_start = td_to_time(start_td)
        prov_end = td_to_time(end_td)
        if time_overlap(form_start, form_end, prov_start, prov_end):
            return False
    return True


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        if 'First_Name' in request.form and 'Last_Name' in request.form and 'Email' in request.form and 'Phone_Number' in request.form and 'City' in request.form and 'State' in request.form and 'Pincode' in request.form and 'Date_Of_Birth' in request.form and 'Password' in request.form and 'confirm_Password' in request.form:

            First_Name = request.form['First_Name']
            Last_Name = request.form['Last_Name']
            Email = request.form['Email']
            Phone_Number = request.form['Phone_Number']
            City = request.form['City']
            State = request.form['State']
            Pincode = request.form['Pincode']
            Date_Of_Birth = request.form['Date_Of_Birth']
            Password = request.form['Password']
            confirm_Password = request.form['confirm_Password']

            if Password != confirm_Password:
                msg = "Passwords do not match!"
                return render_template('signup.html', msg=msg)

            mydb = get_db()
            mycursor = mydb.cursor()
            mycursor.execute('SELECT * FROM customer WHERE First_Name = %s', (First_Name,))
            account = mycursor.fetchone()

            if account:
                msg = 'Account already exists!'
                mycursor.close()
                mydb.close()
                return render_template('signup.html', msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', Email):
                msg = 'Invalid email address!'
                mycursor.close()
                mydb.close()
                return render_template('signup.html', msg=msg)
            elif not re.match(r'[A-Za-z0-9]+', First_Name):
                msg = 'Username must contain only letters and numbers!'
                mycursor.close()
                mydb.close()
                return render_template('signup.html', msg=msg)
            elif not First_Name or not Password or not Email:
                msg = 'Please fill out the form!'
                mycursor.close()
                mydb.close()
                return render_template('signup.html', msg=msg)
            else:
                sql = "INSERT INTO customer (First_Name, Last_Name, Email, Phone_Number,Date_Of_Birth,City,State, Pincode, Password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = [(First_Name, Last_Name, Email, Phone_Number, Date_Of_Birth, City, State, Pincode, Password)]
                mycursor.executemany(sql, val)
                mydb.commit()
                mycursor.close()
                mydb.close()
                msg = 'You have successfully registered!'
                return render_template('index.html')

    return render_template('signup.html', msg=msg)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/service_provider', methods=['GET', 'POST'])
def service_provider():
    msg = ''
    if request.method == 'POST':
        if 'First_Name' in request.form and 'Last_Name' in request.form and 'Email' in request.form and 'Phone_Number' in request.form and 'City' in request.form and 'State' in request.form and 'Pincode' in request.form and 'Date_Of_Birth' in request.form and 'Password' in request.form and 'confirm_Password' in request.form and 'Category' in request.form and 'Base_Price' in request.form:

            First_Name = request.form['First_Name']
            Last_Name = request.form['Last_Name']
            Email = request.form['Email']
            Phone_Number = request.form['Phone_Number']
            City = request.form['City']
            State = request.form['State']
            Pincode = request.form['Pincode']
            Date_Of_Birth = request.form['Date_Of_Birth']
            Password = request.form['Password']
            confirm_Password = request.form['confirm_Password']
            Category = request.form['Category']
            Base_Price = request.form['Base_Price']

            if Password != confirm_Password:
                msg = "Passwords do not match!"
                return render_template('service_provider.html', msg=msg)

            mydb = get_db()
            mycursor = mydb.cursor()
            mycursor.execute('SELECT * FROM service_provider WHERE Email = %s', (Email,))
            account = mycursor.fetchone()

            if account:
                msg = 'Account already exists!'
                mycursor.close()
                mydb.close()
                return render_template('service_provider.html', msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', Email):
                msg = 'Invalid email address!'
                mycursor.close()
                mydb.close()
                return render_template('service_provider.html', msg=msg)
            elif not First_Name or not Password or not Email:
                msg = 'Please fill out the form!'
                mycursor.close()
                mydb.close()
                return render_template('service_provider.html', msg=msg)
            else:
                sql = "INSERT INTO service_provider (First_Name, Last_Name, Email, Phone_Number,Date_Of_Birth,City,State, Pincode, Password,Category, Base_Price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
                val = [(First_Name, Last_Name, Email, Phone_Number, Date_Of_Birth, City, State, Pincode, Password, Category, Base_Price)]
                mycursor.executemany(sql, val)
                mydb.commit()
                mycursor.close()
                mydb.close()
                msg = 'You have successfully registered!'
                return render_template('index.html')

    return render_template('service_provider.html', msg=msg)


@app.route('/services', methods=['GET', 'POST'])
def services():
    category = request.form.get('Category') or request.args.get('category', '')
    result = []
    if category:
        mydb = get_db()
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(
            "SELECT * FROM service_provider WHERE LOWER(Category) LIKE LOWER(%s)",
            (f"%{category.strip()}%",)
        )
        result = mycursor.fetchall()
        mycursor.close()
        mydb.close()
    return render_template('services.html', results=result, category=category)


@app.route('/service_provider_login', methods=['GET', 'POST'])
def service_provider_login():
    msg = None
    if request.method == 'GET':
        return render_template('service_provider_login.html', msg=msg)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        Email = request.form['email']
        Password = request.form['password']

        mydb = get_db()
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM service_provider WHERE Email = %s AND Password = %s', (Email, Password))
        account = mycursor.fetchone()
        mycursor.close()
        mydb.close()
        if account:
            session.clear()
            session['user_id'] = account[0]
            session['role'] = 'provider'
            session['name'] = f"{account[1]} {account[2]}"
            return redirect(url_for('profile'))
        msg = 'Incorrect username/password!'
        return render_template('service_provider_login.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = None
    if request.method == 'GET':
        return render_template('login.html', msg=msg)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        Email = request.form['email']
        Password = request.form['password']

        mydb = get_db()
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM customer WHERE Email = %s AND Password = %s', (Email, Password))
        account = mycursor.fetchone()
        mycursor.close()
        mydb.close()
        if account:
            session.clear()
            session['user_id'] = account[0]
            session['role'] = 'customer'
            session['name'] = f"{account[1]} {account[2]}"
            return redirect(url_for('profile'))
        msg = 'Incorrect username/password!'
        return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required()
def profile():
    """Single entry point for 'View my profile'. Sends the logged-in user
    to the profile page that matches their role, using their own ID from
    the session (never trusts a client-supplied ID)."""
    if session.get('role') == 'provider':
        return redirect(url_for('update_profile', ProviderID=session['user_id']))
    if session.get('role') == 'customer':
        return redirect(url_for('customer_profile', CustomerID=session['user_id']))
    return redirect(url_for('home'))


@app.route('/update_profile/<int:ProviderID>', methods=['GET', 'POST'])
@login_required(role="provider")
def update_profile(ProviderID):
    # A provider may only view/edit their own profile, regardless of what
    # ID appears in the URL.
    if ProviderID != session['user_id']:
        flash("You can only access your own profile.", "error")
        return redirect(url_for('update_profile', ProviderID=session['user_id']))

    if request.method == "GET":
        account = get_data_from_db(ProviderID=ProviderID)
        return render_template('service_provider_profile.html', account=account)

    mydb = get_db()

    if request.method == 'POST':
        if 'First_Name' in request.form and 'Last_Name' in request.form and 'Email' in request.form and 'Phone_Number' in request.form and 'City' in request.form and 'State' in request.form and 'Pincode' in request.form and 'Date_Of_Birth' in request.form and 'Category' in request.form:
            First_Name = request.form['First_Name']
            Last_Name = request.form['Last_Name']
            Email = request.form['Email']
            Phone_Number = request.form['Phone_Number']
            Date_Of_Birth = request.form['Date_Of_Birth']
            City = request.form['City']
            State = request.form['State']
            Pincode = request.form['Pincode']
            Category = request.form['Category']

            mycursor = mydb.cursor()
            mycursor.execute("""
                UPDATE service_provider SET
                    First_Name=%s, Last_Name=%s, Email=%s, Phone_Number=%s,
                    Date_Of_Birth=%s, City=%s, State=%s, Pincode=%s,Category=%s
                WHERE ProviderID=%s
            """, (
                First_Name, Last_Name, Email, Phone_Number, Date_Of_Birth,
                City, State, Pincode, Category, ProviderID
            ))
            mydb.commit()
            mycursor.close()
            mydb.close()
            return redirect(url_for('update_profile', ProviderID=ProviderID))
        mydb.close()
        return redirect(url_for('update_profile', ProviderID=ProviderID))


def get_data_from_db(**kwargs):
    ProviderID = kwargs.get("ProviderID")
    mydb = get_db()
    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM service_provider WHERE ProviderID = %s', (ProviderID,))
    response = mycursor.fetchone()
    mycursor.close()
    mydb.close()
    return response


@app.route('/update_password/<int:ProviderID>', methods=['GET', 'POST'])
@login_required(role="provider")
def update_password(ProviderID):
    if ProviderID != session['user_id']:
        flash("You can only access your own account.", "error")
        return redirect(url_for('update_password', ProviderID=session['user_id']))

    if request.method == "GET":
        account = get_data_from_db(ProviderID=ProviderID)
        return render_template('more_setting.html', account=account)

    if request.method == 'POST':
        mydb = get_db()
        if 'new_password' in request.form and 'confirm_password' in request.form:
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if new_password == confirm_password:
                try:
                    mycursor = mydb.cursor()
                    mycursor.execute("UPDATE service_provider SET Password=%s WHERE ProviderID=%s", (new_password, ProviderID))
                    mydb.commit()
                    mycursor.close()
                    flash('Password updated successfully!', 'success')
                except mysql.connector.Error as err:
                    flash(f'Error updating password: {err}', 'error')
                finally:
                    mydb.close()
            else:
                flash('New password and confirm password are not same!', 'error')
                mydb.close()

        return redirect(url_for('update_password', ProviderID=ProviderID))
    return redirect(url_for('update_password', ProviderID=ProviderID))


@app.route('/customer_profile/<int:CustomerID>', methods=['GET', 'POST'])
@login_required(role="customer")
def customer_profile(CustomerID):
    # A customer may only view/edit their own profile, regardless of what
    # ID appears in the URL.
    if CustomerID != session['user_id']:
        flash("You can only access your own profile.", "error")
        return redirect(url_for('customer_profile', CustomerID=session['user_id']))

    if request.method == 'POST':
        required = ['First_Name', 'Last_Name', 'Email', 'Phone_Number',
                    'City', 'State', 'Pincode', 'Date_Of_Birth']
        if all(field in request.form for field in required):
            First_Name = request.form['First_Name']
            Last_Name = request.form['Last_Name']
            Email = request.form['Email']
            Phone_Number = request.form['Phone_Number']
            Date_Of_Birth = request.form['Date_Of_Birth']
            City = request.form['City']
            State = request.form['State']
            Pincode = request.form['Pincode']

            mydb = get_db()
            mycursor = mydb.cursor()
            mycursor.execute("""
                UPDATE customer SET
                    First_Name=%s, Last_Name=%s, Email=%s, Phone_Number=%s,
                    Date_Of_Birth=%s, City=%s, State=%s, Pincode=%s
                WHERE CustomerID=%s
            """, (
                First_Name, Last_Name, Email, Phone_Number, Date_Of_Birth,
                City, State, Pincode, CustomerID
            ))
            mydb.commit()
            mycursor.close()
            mydb.close()

            # Keep the session display name in sync with any edit.
            session['name'] = f"{First_Name} {Last_Name}"
            flash("Profile updated successfully!", "success")
        return redirect(url_for('customer_profile', CustomerID=CustomerID))

    account = get_customer_by_id(CustomerID)
    return render_template('customer_profile.html', account=account)


@app.route("/hire", methods=["GET", "POST"])
@login_required(role="customer")
def hire():
    provider_id = request.args.get("provider_id") or request.form.get("provider_id")
    if not provider_id:
        flash("Please select a service provider first.", "error")
        return redirect(url_for("home"))

    provider = get_provider_by_id(provider_id)
    if not provider:
        flash("Service provider not found.", "error")
        return redirect(url_for("home"))

    customer = get_customer_by_id(session['user_id'])
    default_name = f"{customer['First_Name']} {customer['Last_Name']}"
    default_address = f"{customer.get('City', '')}, {customer.get('State', '')} {customer.get('Pincode', '')}".strip(", ")

    if request.method == "POST":
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        address = request.form["address"]
        name = request.form.get("name", default_name)

        if start_time >= end_time:
            flash("End time must be after start time.", "error")
            return render_template("hire.html", provider=provider, provider_id=provider_id,
                                   default_name=name, default_address=address)

        form_date = datetime.strptime(date, "%Y-%m-%d").date()
        if form_date < datetime.now().date():
            flash("Booking date cannot be in the past.", "error")
            return render_template("hire.html", provider=provider, provider_id=provider_id,
                                   default_name=name, default_address=address)

        availability = provider.get('Availability_Status', 'Available')
        if availability == 'Offline':
            flash("This provider is currently offline and not accepting bookings.", "error")
            return render_template("hire.html", provider=provider, provider_id=provider_id,
                                   default_name=name, default_address=address)

        if not slot_is_available(int(provider_id), form_date, start_time, end_time):
            flash("Requested time slot is not available. Please choose another time.", "error")
            return render_template("hire.html", provider=provider, provider_id=provider_id,
                                   default_name=name, default_address=address)

        mydb = get_db()
        mycursor = mydb.cursor()
        sql = """
            INSERT INTO bookings
            (CustomerID, ProviderID, Service_Category, Booking_Date, Start_Time, End_Time, Address, Amount, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        """
        values = (
            session['user_id'], provider_id, provider['Category'],
            date, start_time, end_time, address, provider['Base_Price']
        )
        mycursor.execute(sql, values)
        mydb.commit()
        mycursor.close()
        mydb.close()

        flash("Booking submitted successfully! Waiting for provider confirmation.", "success")
        return redirect(url_for("bookings"))

    return render_template("hire.html", provider=provider, provider_id=provider_id,
                           default_name=default_name, default_address=default_address)


@app.route('/bookings')
@login_required(role="customer")
def bookings():
    mydb = get_db()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("""
        SELECT b.*, CONCAT(sp.First_Name, ' ', sp.Last_Name) AS provider_name
        FROM bookings b
        JOIN service_provider sp ON b.ProviderID = sp.ProviderID
        WHERE b.CustomerID = %s
        ORDER BY b.Booking_Date DESC, b.Start_Time DESC
    """, (session['user_id'],))
    rows = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    for row in rows:
        row['Start_Time'] = format_time_value(row['Start_Time'])
        row['End_Time'] = format_time_value(row['End_Time'])

    return render_template('customer_bookings.html', bookings=rows)


@app.route('/provider/bookings')
@login_required(role="provider")
def provider_bookings():
    provider_id = session['user_id']
    mydb = get_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
        SELECT b.*, CONCAT(c.First_Name, ' ', c.Last_Name) AS customer_name
        FROM bookings b
        JOIN customer c ON b.CustomerID = c.CustomerID
        WHERE b.ProviderID = %s
        ORDER BY
            FIELD(b.Status, 'Pending', 'Accepted', 'In Progress', 'Completed', 'Rejected'),
            b.Booking_Date ASC, b.Start_Time ASC
    """, (provider_id,))
    rows = mycursor.fetchall()

    mycursor.execute("""
        SELECT COALESCE(SUM(Amount), 0) AS total FROM bookings
        WHERE ProviderID = %s AND Status = 'Completed'
    """, (provider_id,))
    earnings = mycursor.fetchone()['total']

    mycursor.execute("SELECT Availability_Status FROM service_provider WHERE ProviderID = %s", (provider_id,))
    provider_row = mycursor.fetchone()
    availability = provider_row.get('Availability_Status', 'Available') if provider_row else 'Available'

    mycursor.close()
    mydb.close()

    pending_count = sum(1 for r in rows if r['Status'] == 'Pending')
    upcoming_count = sum(1 for r in rows if r['Status'] in ('Accepted', 'In Progress'))
    completed_count = sum(1 for r in rows if r['Status'] == 'Completed')

    for row in rows:
        row['Start_Time'] = format_time_value(row['Start_Time'])
        row['End_Time'] = format_time_value(row['End_Time'])

    return render_template(
        'provider_bookings.html',
        bookings=rows,
        provider_id=provider_id,
        provider_name=session.get('name', ''),
        earnings=earnings,
        pending_count=pending_count,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        availability=availability,
    )


def _update_booking_status(booking_id, provider_id, new_status, allowed_from):
    mydb = get_db()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(
        "SELECT Status FROM bookings WHERE BookingID = %s AND ProviderID = %s",
        (booking_id, provider_id)
    )
    booking = mycursor.fetchone()
    if not booking:
        mycursor.close()
        mydb.close()
        flash("Booking not found.", "error")
        return redirect(url_for('provider_bookings'))

    if booking['Status'] not in allowed_from:
        mycursor.close()
        mydb.close()
        flash(f"Cannot change status from {booking['Status']} to {new_status}.", "error")
        return redirect(url_for('provider_bookings'))

    mycursor.execute(
        "UPDATE bookings SET Status = %s WHERE BookingID = %s AND ProviderID = %s",
        (new_status, booking_id, provider_id)
    )
    mydb.commit()
    mycursor.close()
    mydb.close()
    flash(f"Booking marked as {new_status}.", "success")
    return redirect(url_for('provider_bookings'))


@app.route('/provider/bookings/<int:booking_id>/accept', methods=['POST'])
@login_required(role="provider")
def accept_booking(booking_id):
    return _update_booking_status(booking_id, session['user_id'], 'Accepted', ['Pending'])


@app.route('/provider/bookings/<int:booking_id>/reject', methods=['POST'])
@login_required(role="provider")
def reject_booking(booking_id):
    return _update_booking_status(booking_id, session['user_id'], 'Rejected', ['Pending'])


@app.route('/provider/bookings/<int:booking_id>/progress', methods=['POST'])
@login_required(role="provider")
def progress_booking(booking_id):
    return _update_booking_status(booking_id, session['user_id'], 'In Progress', ['Accepted'])


@app.route('/provider/bookings/<int:booking_id>/complete', methods=['POST'])
@login_required(role="provider")
def complete_booking(booking_id):
    return _update_booking_status(booking_id, session['user_id'], 'Completed', ['In Progress'])


@app.route('/provider/availability', methods=['POST'])
@login_required(role="provider")
def update_availability():
    status = request.form.get('availability', 'Available')
    if status not in ('Available', 'Busy', 'Offline'):
        flash("Invalid availability status.", "error")
        return redirect(url_for('provider_bookings'))

    mydb = get_db()
    mycursor = mydb.cursor()
    mycursor.execute(
        "UPDATE service_provider SET Availability_Status = %s WHERE ProviderID = %s",
        (status, session['user_id'])
    )
    mydb.commit()
    mycursor.close()
    mydb.close()
    flash(f"Availability updated to {status}.", "success")
    return redirect(url_for('provider_bookings'))


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


@app.route('/services/nearby', methods=['GET'])
@login_required(role="customer")
def services_nearby():

    category  = request.args.get('category', '').strip()
    city      = request.args.get('city', '').strip()
    state     = request.args.get('state', '').strip()
    radius_km = float(request.args.get('radius_km', 50))

    if not category:
        flash("Please provide a service category.", "error")
        return redirect(url_for('services'))

    # Fetch customer's own location (if stored)
    customer = get_customer_by_id(session['user_id'])
    cust_lat = customer.get('Latitude')
    cust_lng = customer.get('Longitude')

    # Build query: always filter by category + availability
    mydb      = get_db()
    mycursor  = mydb.cursor(dictionary=True)

    sql    = """SELECT ProviderID, First_Name, Last_Name, Category, Base_Price,
                       City, State, Pincode, Availability_Status,
                       Latitude, Longitude, Service_Radius,
                       Avg_Rating, Review_Count
                FROM service_provider
                WHERE LOWER(Category) LIKE LOWER(%s)
                  AND Availability_Status != 'Offline'"""
    params = [f"%{category}%"]

    if city:
        sql    += " AND LOWER(City) LIKE LOWER(%s)"
        params.append(f"%{city}%")
    if state:
        sql    += " AND LOWER(State) LIKE LOWER(%s)"
        params.append(f"%{state}%")

    mycursor.execute(sql, tuple(params))
    providers = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    # Distance filter (only when customer coords are available)
    results = []
    for p in providers:
        if cust_lat and cust_lng and p['Latitude'] and p['Longitude']:
            dist = haversine_km(cust_lat, cust_lng, p['Latitude'], p['Longitude'])
            p['distance_km'] = round(dist, 1)
            if dist <= radius_km:
                results.append(p)
        else:
            p['distance_km'] = None
            results.append(p)

    # Sort: providers with distance data first, then by distance
    results.sort(key=lambda x: (x['distance_km'] is None, x['distance_km'] or 0))

    return render_template('services_nearby.html',
                           results=results,
                           category=category,
                           city=city,
                           state=state,
                           radius_km=radius_km,
                           has_location=(cust_lat is not None))


@app.route('/customer/location', methods=['POST'])
@login_required(role="customer")
def update_customer_location():
    """Save customer's lat/lng (sent from browser Geolocation API via JS)."""
    lat = request.form.get('latitude')
    lng = request.form.get('longitude')

    if not lat or not lng:
        flash("Could not detect location.", "error")
        return redirect(request.referrer or url_for('home'))

    mydb     = get_db()
    mycursor = mydb.cursor()
    mycursor.execute(
        "UPDATE customer SET Latitude=%s, Longitude=%s WHERE CustomerID=%s",
        (float(lat), float(lng), session['user_id'])
    )
    mydb.commit()
    mycursor.close()
    mydb.close()
    flash("Location saved! You can now see nearby providers.", "success")
    return redirect(request.referrer or url_for('home'))


@app.route('/provider/location', methods=['POST'])
@login_required(role="provider")
def update_provider_location():
    """Save provider lat/lng and service radius from their settings page."""
    lat    = request.form.get('latitude')
    lng    = request.form.get('longitude')
    radius = request.form.get('service_radius', 25)

    if not lat or not lng:
        flash("Could not detect location.", "error")
        return redirect(url_for('provider_bookings'))

    mydb     = get_db()
    mycursor = mydb.cursor()
    mycursor.execute(
        "UPDATE service_provider SET Latitude=%s, Longitude=%s, Service_Radius=%s WHERE ProviderID=%s",
        (float(lat), float(lng), int(radius), session['user_id'])
    )
    mydb.commit()
    mycursor.close()
    mydb.close()
    flash("Service location updated.", "success")
    return redirect(url_for('provider_bookings'))


# PAYMENT INTEGRATION

ALLOWED_METHODS = ('Cash', 'UPI', 'Card', 'Wallet')

@app.route('/bookings/<int:booking_id>/pay', methods=['GET', 'POST'])
@login_required(role="customer")
def pay_booking(booking_id):
    
    mydb     = get_db()
    mycursor = mydb.cursor(dictionary=True)

    # Verify this booking belongs to the logged-in customer
    mycursor.execute("""
        SELECT b.*, CONCAT(sp.First_Name,' ',sp.Last_Name) AS provider_name
        FROM bookings b
        JOIN service_provider sp ON b.ProviderID = sp.ProviderID
        WHERE b.BookingID=%s AND b.CustomerID=%s
    """, (booking_id, session['user_id']))
    booking = mycursor.fetchone()

    if not booking:
        mycursor.close(); mydb.close()
        flash("Booking not found.", "error")
        return redirect(url_for('bookings'))

    if booking['Payment_Status'] == 'Paid':
        mycursor.close(); mydb.close()
        flash("This booking is already paid.", "info")
        return redirect(url_for('bookings'))

    if booking['Status'] not in ('Accepted', 'In Progress', 'Completed'):
        mycursor.close(); mydb.close()
        flash("Payment is only allowed once the provider has accepted your booking.", "error")
        return redirect(url_for('bookings'))

    if request.method == 'POST':
        method         = request.form.get('payment_method')
        transaction_id = request.form.get('transaction_id', '').strip() or None

        if method not in ALLOWED_METHODS:
            flash("Invalid payment method.", "error")
            return render_template('payment.html', booking=booking)

        # Insert into payments table
        mycursor.execute("""
            INSERT INTO payments
                (BookingID, CustomerID, Amount, Payment_Method, Payment_Status, Transaction_ID)
            VALUES (%s, %s, %s, %s, 'Completed', %s)
            ON DUPLICATE KEY UPDATE
                Payment_Status='Completed', Transaction_ID=VALUES(Transaction_ID),
                Payment_Date=CURRENT_TIMESTAMP
        """, (booking_id, session['user_id'], booking['Amount'], method, transaction_id))

        # Update bookings row for quick status reads
        mycursor.execute("""
            UPDATE bookings
            SET Payment_Status='Paid', Payment_Method=%s
            WHERE BookingID=%s
        """, (method, booking_id))

        mydb.commit()
        mycursor.close()
        mydb.close()

        flash(f"Payment of ₹{booking['Amount']} via {method} recorded successfully!", "success")
        return redirect(url_for('bookings'))

    # GET — render the payment form
    mycursor.close()
    mydb.close()
    return render_template('payment.html', booking=booking, allowed_methods=ALLOWED_METHODS)


@app.route('/provider/payments')
@login_required(role="provider")
def provider_payments():
    """Show a provider their earnings broken down by payment method."""
    mydb     = get_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
        SELECT p.*, b.Booking_Date, b.Service_Category,
               CONCAT(c.First_Name,' ',c.Last_Name) AS customer_name
        FROM payments p
        JOIN bookings b ON p.BookingID = b.BookingID
        JOIN customer c ON p.CustomerID = c.CustomerID
        WHERE b.ProviderID = %s
        ORDER BY p.Payment_Date DESC
    """, (session['user_id'],))
    payments = mycursor.fetchall()

    mycursor.execute("""
        SELECT COALESCE(SUM(p.Amount),0) AS total_earned,
               p.Payment_Method, COUNT(*) AS txn_count
        FROM payments p
        JOIN bookings b ON p.BookingID = b.BookingID
        WHERE b.ProviderID=%s AND p.Payment_Status='Completed'
        GROUP BY p.Payment_Method
    """, (session['user_id'],))
    breakdown = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    total = sum(r['total_earned'] for r in breakdown)
    return render_template('provider_payments.html',
                           payments=payments,
                           breakdown=breakdown,
                           total_earned=total)


@app.route('/bookings/<int:booking_id>/refund', methods=['POST'])
@login_required(role="provider")
def refund_payment(booking_id):
    """Provider can issue a refund on a rejected booking that was already paid."""
    mydb     = get_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute(
        "SELECT * FROM bookings WHERE BookingID=%s AND ProviderID=%s",
        (booking_id, session['user_id'])
    )
    booking = mycursor.fetchone()

    if not booking:
        flash("Booking not found.", "error")
    elif booking['Payment_Status'] != 'Paid':
        flash("No paid payment to refund.", "error")
    elif booking['Status'] != 'Rejected':
        flash("Refunds are only allowed on rejected bookings.", "error")
    else:
        mycursor.execute(
            "UPDATE payments SET Payment_Status='Refunded' WHERE BookingID=%s",
            (booking_id,)
        )
        mycursor.execute(
            "UPDATE bookings SET Payment_Status='Refunded' WHERE BookingID=%s",
            (booking_id,)
        )
        mydb.commit()
        flash("Refund issued successfully.", "success")

    mycursor.close()
    mydb.close()
    return redirect(url_for('provider_bookings'))


#  RATING & REVIEW SYSTEM

@app.route('/bookings/<int:booking_id>/review', methods=['GET', 'POST'])
@login_required(role="customer")
def submit_review(booking_id):
    """
    GET  → show the review form.
    POST → save the rating + text (only for Completed bookings with no existing review).
    """
    mydb     = get_db()
    mycursor = mydb.cursor(dictionary=True)

    # Booking must belong to this customer and be Completed
    mycursor.execute("""
        SELECT b.*, CONCAT(sp.First_Name,' ',sp.Last_Name) AS provider_name,
               sp.ProviderID
        FROM bookings b
        JOIN service_provider sp ON b.ProviderID = sp.ProviderID
        WHERE b.BookingID=%s AND b.CustomerID=%s AND b.Status='Completed'
    """, (booking_id, session['user_id']))
    booking = mycursor.fetchone()

    if not booking:
        flash("You can only review completed bookings.", "error")
        mycursor.close(); mydb.close()
        return redirect(url_for('bookings'))

    # Check if already reviewed
    mycursor.execute("SELECT ReviewID FROM reviews WHERE BookingID=%s", (booking_id,))
    existing = mycursor.fetchone()
    if existing:
        flash("You have already reviewed this booking.", "info")
        mycursor.close(); mydb.close()
        return redirect(url_for('bookings'))

    if request.method == 'POST':
        rating      = request.form.get('rating')
        review_text = request.form.get('review_text', '').strip()

        if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
            flash("Please select a rating between 1 and 5.", "error")
            return render_template('review_form.html', booking=booking)

        mycursor.execute("""
            INSERT INTO reviews (BookingID, CustomerID, ProviderID, Rating, Review_Text)
            VALUES (%s, %s, %s, %s, %s)
        """, (booking_id, session['user_id'], booking['ProviderID'], int(rating), review_text))
        mydb.commit()

        mycursor.close(); mydb.close()
        flash("Thank you for your review!", "success")
        return redirect(url_for('bookings'))

    mycursor.close(); mydb.close()
    return render_template('review_form.html', booking=booking)


@app.route('/provider/<int:provider_id>/reviews')
def provider_reviews(provider_id):
    """Public page showing all reviews for a given provider."""
    mydb     = get_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
        SELECT sp.First_Name, sp.Last_Name, sp.Category,
               sp.Avg_Rating, sp.Review_Count, sp.Base_Price, sp.City, sp.State
        FROM service_provider sp
        WHERE sp.ProviderID = %s
    """, (provider_id,))
    provider = mycursor.fetchone()

    if not provider:
        flash("Provider not found.", "error")
        mycursor.close(); mydb.close()
        return redirect(url_for('home'))

    mycursor.execute("""
        SELECT r.Rating, r.Review_Text, r.Created_At,
               CONCAT(c.First_Name,' ',c.Last_Name) AS customer_name
        FROM reviews r
        JOIN customer c ON r.CustomerID = c.CustomerID
        WHERE r.ProviderID = %s
        ORDER BY r.Created_At DESC
    """, (provider_id,))
    reviews = mycursor.fetchall()

    mycursor.close(); mydb.close()
    return render_template('provider_reviews.html',
                           provider=provider,
                           reviews=reviews,
                           provider_id=provider_id)


@app.route('/services/top-rated')
def top_rated_providers():
    """Browse providers sorted by average rating (highest first)."""
    category = request.args.get('category', '').strip()

    mydb     = get_db()
    mycursor = mydb.cursor(dictionary=True)

    sql = """
        SELECT ProviderID, First_Name, Last_Name, Category,
               Base_Price, City, State, Availability_Status,
               Avg_Rating, Review_Count
        FROM service_provider
        WHERE Availability_Status != 'Offline'
          AND Review_Count > 0
    """
    params = []
    if category:
        sql    += " AND LOWER(Category) LIKE LOWER(%s)"
        params.append(f"%{category}%")

    sql += " ORDER BY Avg_Rating DESC, Review_Count DESC LIMIT 50"
    mycursor.execute(sql, tuple(params))
    providers = mycursor.fetchall()

    mycursor.close(); mydb.close()
    return render_template('top_rated.html', providers=providers, category=category)


if __name__ == '__main__':
    app.run(debug=True)
