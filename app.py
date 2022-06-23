
#Import Dependencies
#In this project, I have chosen to use an sqlite database to store the url - short pairs
import sqlite3
#flask is used as the web framework
from flask import Flask, render_template, request
#string and random are used to generate the short if the user fails to supply it
import string
import random

#create the app
app = Flask(__name__)

#Home
@app.route("/")
def index():
    #Essentially returns the index.html file as a template.
    return render_template("index.html")

#Shortener
@app.route("/run",methods = ['POST', 'GET'])
def shorten():
    #Checks for the right method
    if request.method == 'POST':
        #Gets url
        #avoids fatal error on user not supplying the url
        try:
            url = request.form['url'].split("\n")[0]
        except:
            return "BAD: URL NOT GIVEN"
        #avoids fatal error on user not supplying the url and generates the string for him
        try:
            custom = request.form['url'].split("\n")[1]
        except:
            lst = [random.choice(string.ascii_letters + string.digits) for n in range(15)]
            custom = "".join(lst)
        
        #connect to the database
        db = sqlite3.connect('db/urls.db')
        cursor = db.cursor()

        #avoid duplicate short links (not working as of now)
        try:
            cursor.execute(f"SELECT original FROM urls WHERE shorterned='{url}'")
            return "BAD: SHORT URL ALREADY USED"
        except:
            cursor.execute(f"INSERT INTO urls (original, shorterned) VALUES ('{url}','{custom}')")
            db.commit()
        return "yay"

app.run(host="0.0.0.0")