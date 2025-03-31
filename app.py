import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import res_handler, usr_handler, config

app = Flask(__name__)
app.secret_key = config.secret_key

# main page
@app.route("/")
def index():
    reservations = res_handler.get_reservations()
    return render_template("index.html", reservations=reservations)

# show a reservation
@app.route("/reservation/<int:reservation_id>")
def show_reservation(reservation_id):
    reservation = res_handler.get_reservation(reservation_id)
    return render_template("reservation.html", reservation=reservation)

# new reservation
@app.route("/new_reservation", methods=["POST"])
def new_reservation():
    title = request.form["title"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    place = request.form["place"]
    user_id = session["user_id"]

    reservation_id = res_handler.add_reservation(title, start_time, end_time, place, user_id)
    return redirect("/reservation/" + str(reservation_id))

# edit reservation
@app.route("/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    reservation = res_handler.get_reservation(reservation_id)

    if request.method == "GET":
        return render_template("edit.html", reservation=reservation)

    if request.method == "POST":
        new_title = request.form["title"]
        new_start_time = request.form["start_time"]
        new_end_time = request.form["end_time"]
        new_place = request.form["place"]
        res_handler.update_reservation(reservation["id"], new_title, new_start_time, new_end_time, new_place)
        return redirect(f"/reservation/{str(reservation["id"])}")

# remove reservation
@app.route("/remove/<int:reservation_id>", methods=["GET", "POST"])
def remove_reservation(reservation_id):
    reservation = res_handler.get_reservation(reservation_id)

    if request.method == "GET":
        return render_template("remove.html", reservation=reservation)

    if request.method == "POST":
        if "remove" in request.form:
            res_handler.remove_reservation(reservation["id"])
            return redirect("/")
        elif "cancel" in request.form:
            return redirect(f"/reservation/{reservation_id}")

# register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password_1 = request.form["password_1"]
        password_2 = request.form["password_2"]

        if password_1 != password_2:
            return "Passwords do not match"

        # check if the username already exists
        if usr_handler.find_user(username):
            return("Username already exists!")

        usr_handler.create_user(username, password_1)
        return "Account created"

# log in
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = usr_handler.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            return redirect("/")
        else:
            return "Incorrect username or password"

# logout
@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")

# search
@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    query_match_all = f"%{query}%"
    reservations = res_handler.get_reservations(r_title=query_match_all)
    return render_template("search.html", query=query, reservations=reservations)