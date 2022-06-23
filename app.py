DOMAIN = "https://www.mulberry.com/url/" #For production deployment

#Import Dependencies
#In this project, I chose to use a sqlite database to store the (url-shortened) pairs
import sqlite3
#Flask is used as the web framework
from flask import Flask, redirect, render_template, request
#String and Random are used to generate the short if the user fails to supply it
import string
import random

#Create the app
app = Flask(__name__)

#Home
@app.route("/")
def index():
    #Essentially returns the index.html file as a template. Nothing special.
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
            if "http" not in url:
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
        cursor.execute(f"SELECT shorterned FROM urls WHERE shorterned='{custom}'")
        if str(cursor.fetchall()) == "[]":
            cursor.execute(f"INSERT INTO urls (original, shorterned) VALUES ('{url}','{custom}')")
            db.commit()
            return render_template("result.html", shortlink= (DOMAIN + str(custom) + "/") )
        else:
            print(cursor.fetchall())
            return render_template("error.html", error="Sorry, shortlink already exists in our database, please choose another!")

# TO IMPLEMENT: The actual return_redirect when a user uses a short url, also the url checking is pretty shit...
# this should work https://riptutorial.com/flask/example/19420/catch-all-route

@app.route('/url', defaults={'u_path': ''})
@app.route('/url/<path:u_path>')
def catch_all(u_path):
    pointer = u_path.replace("/","")
    db = sqlite3.connect('db/urls.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT original FROM urls WHERE shorterned='{pointer}'")
    originalURL = cursor.fetchall()[0][0].strip()
    
    return redirect(originalURL)

# Run app for debug
app.run(host="0.0.0.0")