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



@app.route("/addcar", methods=["GET", "POST"])
def addcar():
    if request.method == "POST":
        car = {
            "car_name": request.form.get("car_name"),
            "car_country": request.form.get("car_country"),
            "car_description": request.form.get("car_description"),
            "date": request.form.get("date"),
            "car_image": request.form.get("car_image"),
            "created_by": session["user"]
        }
        mongo.db.car.insert_one(car)
        flash("Car Successfully Added")
        return redirect(url_for("addcar"))
    cars = mongo.db.car_cat.find().sort("car_name", 1)
    return render_template("addcar.html", car=cars)


@app.route("/addcar/<addcar_id>/edit", methods=["GET", "POST"])
def edit_car(car_id):
    if request.method == "POST":
        submit = {
            "car_name": request.form.get("car_name"),
            "car_country": request.form.get("car_country"),
            "car_description": request.form.get("car_description"),
            "date": request.form.get("date"),
            "car_image": request.form.get("car_image"),
            "created_by": session["user"]
        }
        mongo.db.car.update({"_id": ObjectId(car_id)}, submit)
        flash("Car Successfully Updated")
    cars = mongo.db.cars.find_one({"_id": ObjectId(car_id)})
    cars = mongo.db.car_cat.find().sort("car_name", 1)
    return render_template(
        "edit_car.html", car=cars)


@app.route("/addcar/<car_id>/delete")
def delete_car(car_id):
    mongo.db.cars.remove({"_id": ObjectId(car_id)})
    flash("Car Successfully Deleted")
    return redirect(url_for("addcar"))



@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks {}, we have received your message!".format(
            request.form.get("name")))
    return render_template("contact.html", page_title="Contact")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))
    


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT")),
        debug=True) #change to false before submit