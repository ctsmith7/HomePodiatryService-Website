from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_session import Session
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# mysql.connector simple connect func
def db_connect():
    try:
        conn = mysql.connector.connect(
            host = "",
            user = "",
            password = "",
            database = ""
        )
        return conn
    except mysql.connector.Error as e:
        pass


#home page
@app.route('/')
def index():
    return render_template('index.html')


#about page
@app.route('/about')
def about():
    return render_template('about.html')


#contact page
@app.route('/contact', methods=["GET", "POST"])
def contact():
    return render_template('contact.html')

@app.route('/contact_handle', methods=["GET", "POST"])
def contact_handle():
    if request.method == 'POST':
        first = request.form.get("inputFirst")
        last = request.form.get("inputLast")
        email = request.form.get("inputEmail")
        phone = request.form.get("inputPhone")
        zip = request.form.get("inputZip")
        service_desc = request.form.get("inputComment")

        insert_request(first, last, email, phone, zip, service_desc)

        return render_template('contact.html', message = "Your Contact Request has been submitted. Please allow up to 72 hours for a response.")
    else:
        return render_template('contact.html', message = "Error... Something went wrong. Please reload the page.")

def insert_request(first, last, email, phone, zip, service_desc):
    conn = db_connect()
    mycursor = conn.cursor()

    query = "INSERT INTO Requests (first_name, last_name, email, phone, zip, service_description) VALUES (%s, %s, %s, %s, %s, %s);"
    values = (first, last, email, phone, zip, service_desc)
    mycursor.execute(query, values)
    conn.commit()

    conn.close()

@app.route('/contact_handle_old', methods=["GET", "POST"])
def contact_handle_old():
    if request.method == 'POST':
        first = request.form.get("inputFirst")
        last = request.form.get("inputLast")
        email = request.form.get("inputEmail")
        phone = request.form.get("inputPhone")
        zip = request.form.get("inputZip")
        comment = request.form.get("inputComment")

        message = "Your Appointment Request has been submitted. Thank You!"
        mailer(email, "Home Podiatry Service - Appointment Request", message)

        message = "New Patient Info\n\nName: {} {}\nE-mail: {}\nPhone Number: {}\nZip Code: {}\n\nComment/Description of Issue:\n{}".format(first, last, email, phone, zip, comment)
        mailer("", "Home Podiatry Service - Appointment Request", message)

        return render_template('contact.html', message = "Your Appointment Request has been submitted. A confirmation email has been sent to your inbox.")
    else:
        return render_template('contact.html', message = "Error... Something went wrong. Please reload the page.")

def mailer(email, subject, message):
    msg = MIMEMultipart()
    msg["From"] = ""
    msg["To"] = email
    msg["Cc"] = ""
    msg["Subject"] = subject
    msg.attach(MIMEText(message))

    smtp = smtplib.SMTP("smtp-mail.outlook.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login("", "")
    smtp.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
    smtp.quit()


#admin page
@app.route('/admin', methods=["GET", "POST"])
def admin():
    try:
        if session["name"] == None:
            return redirect(url_for('login'))
        elif session["name"] == "admin":
            requests = db_getAll("Requests")
            curr_appts = db_getAll("Appointments")
            return render_template('admin.html', requests = requests, curr_appts = curr_appts)
    except:
        return redirect(url_for('login'))

def db_getAll(table):
    try:
        conn = db_connect()
        mycursor = conn.cursor()

        mycursor.execute(f"SELECT * FROM {table}")

        results = mycursor.fetchall()
    except mysql.connector.Error as e:
        results = ["#"]

    conn.close()
    return results

@app.route('/login', methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        pass_input = request.form.get("admin_pass")
        if pass_input == "":
            session["name"] = "admin"
            return redirect(url_for('admin'))
        else:
            message = "Password Incorrect"
    return render_template('login.html', message = message)

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect(url_for('index'))


#404 handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
