import os
import json
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mongoengine import MongoEngine
if os.path.exists("env.py"):
    import env



app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    data = []
    with open("data/cars.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("about.html", page_title="About", cars=data)


@app.route("/about/<car_name>")
def about_car(car_name):
    car = {}
    with open("data/cars.json", "r") as json_data:
        data = json.load(json_data)
        for obj in data:
            if obj["url"] == car_name:
                car = obj
    return render_template("car.html", car=car)


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    tasks = mongo.db.tasks.find()
    return render_template("tasks.html", tasks=tasks)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks {}, we have received your message!".format(
            request.form.get("name")))
    return render_template("contact.html", page_title="Contact")


@app.route("/signup")
def signup():
    return render_template("signup.html", page_title="signup")


@app.route("/login")
def login():
    return render_template("login.html", page_title="Login")


@app.route("/logout")
def logout():
    return render_template("logout.html", page_title="Logout")


@app.route("/addcar")
def addcar():
    if request.method == 'POST':
        from Ipython import embed; embed()
    return render_template("addcar.html", page_title="Add Car")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT")),
        debug=True) #change to false before submit