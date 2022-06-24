DOMAIN = "/url/" #For production deployment

#Import Dependencies
#In this project, I chose to use a sqlite database to store the (url-shortened) pairs
import sqlite3
#General OS Import
import os
import click
#Flask is used as the web framework
from flask import Flask, redirect, render_template, request, make_response, send_from_directory
#String and Random are used to generate the short if the user fails to supply it
import string
import random


#Create the app
app = Flask(__name__)

#Favicon
@app.route('/favicon.ico')
def favicon():
    #StackOverflow
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico',mimetype='image/vnd.microsoft.icon')

#Home
@app.route("/")
def index():
    #Essentially returns the index.html file as a template.
    return render_template("index.html")

#Shortener
@app.route("/run",methods = ['POST', 'GET'])
def shorten():
    #Checks for the right method
    if request.method == 'GET':
        return render_template("error.html", error="NO DATA GIVEN. Please access this page only by clicking the button on our home page.")
    if request.method == 'POST':

        #avoids fatal error on user not supplying the url
        try:
            url = request.form['url'].split("\n")[0]
            if "http" not in url or "://" not in url:
                raise Exception("")
        except:
            return render_template("error.html", error="URL NOT GIVEN")

        #avoids fatal error on user not supplying the url and generates the string for him
        try:
            custom = request.form['url'].split("\n")[1]
            #remove the user's pesky spaces and stupid newlines
            custom = custom.replace(" ", "-")
            custom = custom.strip()
        except:
            #generate a 15 char long random string, and no, too lazy for symbols
            lst = [random.choice(string.ascii_letters + string.digits) for n in range(15)]
            custom = "".join(lst)
        
        #additional checks go here
        if custom == "" or custom == " " or "\n" in custom:
            return render_template("error.html", error="Sorry, there was an unexpected error.")

        #connect to the database
        db = sqlite3.connect('db/urls.db')
        cursor = db.cursor()

        #avoid duplicate short links (it works now, i fixed it, yay I guess [Do not touch it])
        cursor.execute(f"SELECT shortened FROM urls WHERE shortened='{custom}'")
        if str(cursor.fetchall()) == "[]":
            cursor.execute(f"INSERT INTO urls (original, shortened, clicks) VALUES ('{url}','{custom}',0)")
            db.commit()
            return render_template("result.html", shortlink= (DOMAIN + str(custom) + "/") )
        else:
            print(cursor.fetchall())
            return render_template("error.html", error="Sorry, shortlink already exists in our database, please choose another!")

#When the user requests a short link
@app.route('/url', defaults={'u_path': ''})
@app.route('/url/<path:u_path>')
def catch_all(u_path):
    #Our shortened link
    pointer = u_path.replace("/","")
    db = sqlite3.connect('db/urls.db')
    cursor = db.cursor()
    #Increment Clicks
    cursor.execute(f"SELECT clicks FROM urls WHERE shortened='{pointer}'")
    clicksOriginal = int(cursor.fetchall()[0][0])
    clicksNew = clicksOriginal + 1
    cursor.execute(f"UPDATE urls SET clicks={clicksNew} WHERE shortened='{pointer}'")
    db.commit()    
    #Get the original
    cursor.execute(f"SELECT original FROM urls WHERE shortened='{pointer}'")
    #Strip the carriage return
    originalURL = cursor.fetchall()[0][0].strip()
    #Redirect to the original url
    return redirect(originalURL)

#admin login
@app.route('/admin',methods = ['POST', 'GET'])
def admin():
    #Standard Login
    if request.method == "GET":
        return render_template("admin.html")
    #Shitty Authentication
    elif request.method == "POST":
        if request.form['email'] == "admin@admin.com" and request.form['password'] == "admin123":
            resp = make_response(redirect("/portal"))
            #more bad auth
            resp.set_cookie('auth', "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9")
            return resp
        else:
            return render_template("error.html", error="Wrong Credentials") 

#admin portal 
@app.route("/portal",methods=["GET","POST"])
def portal():
    if request.method == "GET":
        #Shitty auth
        if request.cookies.get('auth') == "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9":
            return render_template("portal.html")
        else:
            return render_template("error.html",error="403 Forbidden"), 403
    #Execute admin commands
    if request.method == "POST":
        statement = request.form["command"]
        db = sqlite3.connect('db/urls.db')
        cursor = db.cursor()
        try:
            cursor.execute(statement)
            db.commit()
            results = str(cursor.fetchall())
        except sqlite3.OperationalError as error:
            return render_template("error.html",error=error)
        return render_template("message.html", message="Success!", message2=results)

# Run app for debug
app.run(host="0.0.0.0",port=80)
# I love port 80!