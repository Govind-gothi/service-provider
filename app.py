from flask import Flask, render_template, request,url_for,redirect,flash
import mysql.connector
import re
from datetime import datetime, time

app = Flask(__name__)
app.secret_key = ' '

@app.route('/signup', methods=['GET','POST'])
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
                        
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="54321",
            database="user_db"
            )
            mycursor = mydb.cursor()
            mycursor.execute('SELECT * FROM customer WHERE First_Name = %s', (First_Name,))
            account = mycursor.fetchone()

            if account:
                msg = 'Account already exists!'
                return render_template('signup.html', msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', Email):
                msg = 'Invalid email address!'
                return render_template('signup.html', msg=msg)
            elif not re.match(r'[A-Za-z0-9]+', First_Name):
                msg = 'Username must contain only letters and numbers!'
                return render_template('signup.html', msg=msg)

            elif not First_Name or not Password or not Email:
                msg = 'Please fill out the form!'
                return render_template('signup.html', msg=msg)
            else:
                sql = "INSERT INTO customer (First_Name, Last_Name, Email, Phone_Number,Date_Of_Birth,City,State, Pincode, Password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = [(First_Name, Last_Name, Email, Phone_Number,Date_Of_Birth,City, State,Pincode, Password)]
                mycursor.executemany(sql, val)
                mydb.commit()
                msg = 'You have successfully registered!'
                return render_template('index.html')
        
    return render_template('signup.html', msg=msg)


@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     msg = None
#     account = None
#     if request.method=='GET':
#         return render_template('login.html',msg=msg)
#     if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
#         Email = request.form['email']
#         Password = request.form['password']

#         mydb = mysql.connector.connect(
#             host="127.0.0.1",
#             port="3306",
#             user="root",
#             password="54321",
#             database="user_db"
#         )
#         mycursor = mydb.cursor()
#         mycursor.execute('SELECT * FROM customer WHERE Email = %s AND Password = %s', (Email, Password))
#         account = mycursor.fetchone()
#     if account:
#         return render_template('customer_profile.html',account=account)
#     else:
#         msg = 'Incorrect username/password!' 
#         return render_template('login.html', msg=msg)     

    
@app.route('/Service_Provider', methods=['GET', 'POST'])
def Service_Provider():
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
                return render_template('Service_Provider.html', msg=msg)
                        
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="54321",
            database="user_db"
            )
            mycursor = mydb.cursor()
            mycursor.execute('SELECT * FROM Service_Provider WHERE Email = %s', (Email,))
            account = mycursor.fetchone()

            if account:
                msg = 'Account already exists!'
                return render_template('Service_Provider.html', msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', Email):
                msg = 'Invalid email address!'
                return render_template('Service_Provider.html', msg=msg)
            elif not re.match(r'[A-Za-z0-9]+', Email):
                msg = 'Username must contain only letters and numbers!'
                return render_template('Service_Provider.html', msg=msg)

            elif not First_Name or not Password or not Email:
                msg = 'Please fill out the form!'
                return render_template('Service_Provider.html', msg=msg)
            else:
                sql = "INSERT INTO Service_Provider (First_Name, Last_Name, Email, Phone_Number,Date_Of_Birth,City,State, Pincode, Password,Category, Base_Price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
                val = [(First_Name, Last_Name, Email, Phone_Number, Date_Of_Birth,City, State, Pincode, Password, Category, Base_Price)]
                mycursor.executemany(sql, val)
                mydb.commit()
                msg = 'You have successfully registered!'
                return render_template('index.html')
        
    return render_template('Service_Provider.html', msg=msg)


@app.route('/services', methods=['POST'])
def services():
    result = ""
    if request.method == 'POST' and 'Category' in request.form:
        if 'Category' in request.form:
            Category = request.form['Category']
            mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="54321",
            database="user_db"
            )
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute('SELECT * FROM Service_Provider WHERE Category = %s', (Category,))
            result = mycursor.fetchall()
        return render_template('services.html',results=result)
    


@app.route('/service_provider_login', methods=['GET', 'POST'])
def service_provider_login():
    msg = None
    account = None
    if request.method == 'GET':
        return render_template('service_provider_login.html', msg=msg) 
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        Email = request.form['email']
        Password = request.form['password']

        mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="54321",
            database="user_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM Service_Provider WHERE Email = %s AND Password = %s', (Email, Password))
        account = mycursor.fetchone()
    if account:
        return render_template('service_provider_profile.html',account=account)
    else:
        msg = 'Incorrect username/password!' 
        return render_template('service_provider_login.html', msg=msg)     
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = None
    account = None
    if request.method=='GET':
        return render_template('login.html',msg=msg)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        Email = request.form['email']
        Password = request.form['password']

        mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="54321",
            database="user_db"
        )
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM customer WHERE Email = %s AND Password = %s', (Email, Password))
        account = mycursor.fetchone()
    if account:
        return render_template('customar_profile.html',account=account)
    else:
        msg = 'Incorrect username/password!' 
        return render_template('login.html', msg=msg)  
    

@app.route('/update_profile/<int:ProviderID>', methods=['GET','POST'])
def update_profile(ProviderID):
    if request.method == "GET":
        account = get_data_from_db(ProviderID=ProviderID)
        return render_template('service_provider_profile.html', account=account)

    mydb = mysql.connector.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        password="54321",
        database="user_db"
    )
    
    if request.method == 'POST':
        if 'First_Name' in request.form and 'Last_Name' in request.form and 'Email' in request.form and 'Phone_Number' in request.form and 'City' in request.form and 'State' in request.form and 'Pincode' in request.form and 'Date_Of_Birth' in request.form and 'Category' in request.form:
        # Get form data
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
            """,
            (
                First_Name, Last_Name, Email, Phone_Number, Date_Of_Birth,
                City, State, Pincode, Category, ProviderID
            ))
            mydb.commit()
            mycursor.close()
            return redirect(url_for('update_profile', ProviderID=ProviderID))
        return redirect(url_for('update_profile', ProviderID=ProviderID))

def get_data_from_db(**kwargs):
    ProviderID = kwargs.get("ProviderID")
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        password="54321",
        database="user_db"
    )
    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM Service_Provider WHERE ProviderID = %s', (ProviderID,))
    response = mycursor.fetchone()
    mycursor.close()
    return response


@app.route('/update_password/<int:ProviderID>', methods=['GET', 'POST'])
def update_password(ProviderID):
    if request.method == "GET":
        # Get user data from DB to pre-fill or display on the form
        account = get_data_from_db(ProviderID=ProviderID)
        return render_template('more_setting.html', account=account)

    # Handle POST request: Process the form submission
    if request.method == 'POST':
        # Establish database connection
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            port="3306",
            user="root",
            password="54321",
            database="user_db"
        )
        if 'new_password' in request.form and 'confirm_password' in request.form:
            # Get form data for new password and confirmation
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            # Check if new_password and confirm_password are the same
            if new_password == confirm_password:
                try:
                    mycursor = mydb.cursor()
                    # Execute the update query
                    mycursor.execute("UPDATE service_provider SET Password=%s WHERE ProviderID=%s", (new_password, ProviderID))
                    mydb.commit() 
                    mycursor.close()
                    flash('Password updated successfully!', 'success')
                    print(f"Password for ProviderID {ProviderID} updated successfully.")
                except mysql.connector.Error as err:
                    # Handle database errors
                    print(f"Error: {err}")
                    # Add an error message here
                    flash(f'Error updating password: {err}', 'danger')
                finally:
                    mydb.close() # Close the database connection
            else:
                # Passwords do not match
                print("New password and confirm password do not match.")
                flash('New password and confirm password are not same!', 'danger')

        return redirect(url_for('update_password', ProviderID=ProviderID))
    return redirect(url_for('update_password', ProviderID=ProviderID))

def td_to_time(td):
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    h %= 24  # wrap around for times > 24 hours
    return time(h, m)

def time_overlap(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)

@app.route("/hire", methods=["GET", "POST"])
def hire():    
    if request.method == "POST":
        if 'name' in request.form and 'date' in request.form and 'start_time' in request.form and 'end_time' in request.form and 'address' in request.form : 
            name = request.form["name"]
            date = request.form["date"]
            start_time = request.form["start_time"]
            end_time = request.form["end_time"]

            
            address = request.form["address"]
            provider_id = request.form["provider_id"]
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="54321",
                database="user_db"
                )
            mycursor = mydb.cursor()
            hired_query = "SELECT * FROM hire WHERE provider_id = %s"
            values = (provider_id,)
            mycursor.execute(hired_query,values)
            result = mycursor.fetchall()
            
            form_date = datetime.strptime(date, "%Y-%m-%d").date()
            form_start = datetime.strptime(start_time, "%H:%M").time()
            form_end = datetime.strptime(end_time, "%H:%M").time()
            
            available_slots = []
            not_available = False

            for entry in result:
                entry_date = entry[2]
                start_td = entry[3]
                end_td = entry[4]

                if entry_date != form_date:
                    continue  # skip other dates
            

                prov_start = td_to_time(start_td)
                prov_end = td_to_time(end_td)

                if time_overlap(form_start, form_end, prov_start, prov_end):
                    not_available = True
                else:
                    available_slots.append((prov_start, prov_end))

            if not_available:
                flash("❌ Requested slot is NOT available.", "error")
                if available_slots:
                    flash("❌ Other available slots on that date:", "error")
                    for s, e in available_slots:
                        print(s.strftime("%H:%M"), "-", e.strftime("%H:%M"))
                else:
                     flash("❌ No other slots available on that date.", "error")
            else:                
                flash("✅ Booking Successful!")
                sql = "INSERT INTO hire (provider_id,name, date, start_time, end_time, address) VALUES (%s,%s, %s, %s, %s, %s)"
                values = (provider_id,name, date, start_time, end_time, address)
                mycursor.execute(sql, values)
                mydb.commit()
                    

            

            flash("✅ Booking Successful!")
            return redirect(url_for("hire"))

            # return redirect("/hire")
    provider_id = request.args.get("provider_id")
    return render_template("hire.html",provider_id= provider_id)



if __name__ == '__main__':
    app.run(debug=True)


