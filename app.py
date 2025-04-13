import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import res_handler, usr_handler, tag_handler, config

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
    reservation = res_handler.get_reservations(r_id=reservation_id)[0]
    tags = tag_handler.get_tags(reservation_id)
    return render_template("reservation.html", reservation=reservation, tags=tags)

# new reservation
@app.route("/new-reservation", methods=["GET", "POST"])
def new_reservation():
    if request.method == "GET":
        allowed_tags = tag_handler.get_allowed()
        return render_template("new-reservation.html", allowed_tags=allowed_tags)

    if request.method == "POST":
        user_id = session["user_id"]

        # get form information
        title = request.form["title"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        place = request.form["place"]
        tags = request.form.getlist("tag")

        # create the reservation
        reservation_id = res_handler.add_reservation(title, start_time, end_time, place, user_id)
        
        # add tags
        for tag in tags:
            tag_handler.add_tag(tag, reservation_id)
        
        # redirect to the reservation
        return redirect("/reservation/" + str(reservation_id))

# edit reservation
@app.route("/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    reservation = res_handler.get_reservations(r_id=reservation_id)[0]

    if request.method == "GET":
        allowed_tags = tag_handler.get_allowed()
        tags = tag_handler.get_tags(reservation_id)
        return render_template("edit.html", reservation=reservation, allowed_tags=allowed_tags, tags=tags)

    if request.method == "POST":
        # get form information
        new_title = request.form["title"]
        new_start_time = request.form["start_time"]
        new_end_time = request.form["end_time"]
        new_place = request.form["place"]
        tags = request.form.getlist("tag")

        # remove old tags and add new
        tag_handler.remove_tag("%", reservation_id)
        for tag in tags:
            tag_handler.add_tag(tag, reservation_id)

        # update the reservation
        res_handler.update_reservation(reservation["id"], new_title, new_start_time, new_end_time, new_place)
        
        # redirect to the reservation
        return redirect(f"/reservation/{str(reservation["id"])}")

# remove reservation
@app.route("/remove/<int:reservation_id>", methods=["GET", "POST"])
def remove_reservation(reservation_id):
    reservation = res_handler.get_reservations(r_id=reservation_id)[0]

    if request.method == "GET":
        return render_template("remove.html", reservation=reservation)

    if request.method == "POST":
        if "remove" in request.form:
            tag_handler.remove_tag("%", reservation_id)
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