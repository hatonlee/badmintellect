import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort, make_response, flash, url_for
import res_handler, usr_handler, tag_handler, com_handler, enr_handler, config
import secrets, markupsafe
from datetime import datetime, timedelta
import math

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if not session.get("user_id"):
        abort(401)

def check_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(403)

def require_owner(user_id):
    if user_id != session.get("user_id"):
        abort(403)

def require_modify(user_id):
    if int(user_id) != session.get("user_id") and session.get("user_role") != "badmin":
        abort(403)

def is_valid_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_valid_time(time):
    try:
        datetime.strptime(time, "%H:%M")
        return True
    except ValueError:
        return False

def parse_duration(duration):
    try:
        hours, minutes = map(int, duration.split(":"))
        return timedelta(hours=hours, minutes=minutes)
    except (ValueError, TypeError):
        return None

def is_valid_duration(duration, min_duration="00:30", max_duration="06:00"):
    duration = parse_duration(duration)
    if duration is None:
        return False

    min_duration = parse_duration(min_duration)
    max_duration = parse_duration(max_duration)
    return min_duration <= duration <= max_duration

@app.template_filter()
def show_newlines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br>")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    # pagination
    page_size = 25
    reservation_count = res_handler.reservation_count()
    page_count = math.ceil(reservation_count / page_size)
    page_count = max(page_count, 1)

    # navigation
    page = int(request.args.get("page", 1))
    page = max(1, min(page_count, page))

    reservations = res_handler.get_reservations(page=page, page_size=page_size)
    return render_template("index.html", reservations=reservations, page=page, page_count=page_count)

@app.route("/reservation/<int:reservation_id>")
def reservation(reservation_id):
    reservation = res_handler.get_reservation(reservation_id)
    if not reservation:
        abort(404)

    params = {}
    params["reservation"] = reservation

    # show the reservation page
    if request.method == "GET":
        # comment pagination
        page_size = 10
        comment_count = com_handler.comment_count(reservation_id)
        page_count = math.ceil(comment_count / page_size)
        page_count = max(page_count, 1)

        # navigation
        page = int(request.args.get("page", 1))
        page = max(1, min(page_count, page))

        params["tags"] = tag_handler.get_tags(reservation_id)
        params["comments"] = com_handler.get_comments(reservation_id, page=page, page_size=page_size)
        params["is_enrolled"] = enr_handler.is_enrolled(session.get("user_id"), reservation_id)
        params["enrolled_count"] = enr_handler.enrolled_users_count(reservation_id)

        return render_template("reservation.html", page=page, page_count=page_count, **params)

@app.route("/reservation/<int:reservation_id>/add-comment", methods=["POST"])
def add_comment(reservation_id):
    require_login()
    check_csrf()

    # get form information
    comment = request.form["comment"]

    # input validation
    if not comment or len(comment) > 1000:
        abort(400)

    comment = comment.strip()
    comment_id = com_handler.add_comment(reservation_id, session.get("user_id"), comment)

    return redirect(url_for("reservation", reservation_id=reservation_id))

@app.route("/reservation/<int:reservation_id>/remove-comment", methods=["POST"])
def remove_comment(reservation_id):
    require_login()
    check_csrf()

    # get form information
    comment_id = request.form["comment_id"]

    # only commenter or badmin can remove the comment
    comment = com_handler.get_comment(comment_id)

    com_handler.remove_comment(comment_id)
    return redirect(url_for("reservation", reservation_id=reservation_id))

@app.route("/reservation/<int:reservation_id>/enroll", methods=["POST"])
def enroll(reservation_id):
    require_login()
    check_csrf()

    # get form information
    value = request.form["enroll_button"]

    if value == "enroll":
        enr_handler.enroll_user(session.get("user_id"), reservation_id)
        flash("Enrolled succesfully", "success")

    if value == "unenroll":
        enr_handler.unenroll_users(session.get("user_id"), reservation_id)
        flash("Unenrolled succesfully", "success")

    return redirect(url_for("reservation", reservation_id=reservation_id))

@app.route("/new-reservation", methods=["GET", "POST"])
def new_reservation():
    require_login()

    if request.method == "GET":
        allowed_tags = tag_handler.get_allowed_tags()
        return render_template("new-reservation.html", allowed_tags=allowed_tags)

    if request.method == "POST":
        check_csrf()

        # get form information
        params = {"user_id": session.get("user_id")}
        params.update({k: v for k, v in request.form.items() if v.strip()})
        params.pop("tag", None)
        params.pop("csrf_token", None)

        tags = request.form.getlist("tag")

        # input validation
        if (not all((params["title"], params["place"], params["date"], params["time"], params["duration"])) or
            len(params["title"]) > 50 or len(params["place"]) > 50 or
            not is_valid_date(params["date"]) or
            not is_valid_time(params["time"]) or
            not is_valid_duration(params["duration"])):
            abort(400)

        # strip whitespace
        params["title"] = params["title"].strip()
        params["place"] = params["place"].strip()

        reservation_id = res_handler.add_reservation(params=params)

        # add tags
        for tag in tags:
            if tag_handler.is_allowed(tag):
                tag_handler.add_tag(reservation_id, tag)

        flash("Reservation added succesfully", "success")
        return redirect(url_for("reservation", reservation_id=reservation_id))

@app.route("/reservation/<int:reservation_id>/edit", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    require_login()

    reservation = res_handler.get_reservation(reservation_id)
    if not reservation:
        abort(404)

    require_owner(reservation["user_id"])

    if request.method == "GET":
        allowed_tags = tag_handler.get_allowed_tags()
        tags = tag_handler.get_tags(reservation_id)
        return render_template("edit-reservation.html", reservation=reservation, allowed_tags=allowed_tags, tags=tags)

    if request.method == "POST":
        check_csrf()

        # get form information
        params = {k: v for k, v in request.form.items() if v.strip()}
        params["reservation_id"] = reservation_id
        params.pop("tag", None)
        params.pop("csrf_token", None)

        tags = request.form.getlist("tag")

        # input validation
        if (not all((params["title"], params["place"], params["date"], params["time"], params["duration"])) or
            len(params["title"]) > 50 or len(params["place"]) > 50 or
            not is_valid_date(params["date"]) or
            not is_valid_time(params["time"]) or
            not is_valid_duration(params["duration"])):
            abort(400)

        params["title"] = params["title"].strip()
        params["place"] = params["place"].strip()

        res_handler.update_reservation(params=params)

        # update tags
        tag_handler.remove_tags(reservation_id, "%")
        for tag in tags:
            if tag_handler.is_allowed(tag):
                tag_handler.add_tag(reservation_id, tag)

        flash("Reservation edited succesfully", "success")
        return redirect(url_for("reservation", reservation_id=reservation_id))

@app.route("/reservation/<int:reservation_id>/remove", methods=["GET", "POST"])
def remove_reservation(reservation_id):
    require_login()

    reservation = res_handler.get_reservation(reservation_id)
    if not reservation:
        abort(404)

    require_modify(reservation["user_id"])

    if request.method == "GET":
        return render_template("remove-reservation.html", reservation=reservation)

    if request.method == "POST":
        check_csrf()

        action = request.form["remove"]
        if action == "Remove":
            tag_handler.remove_tags(reservation_id, "%")
            com_handler.remove_comments(reservation_id)
            enr_handler.unenroll_users("%", reservation_id)
            res_handler.remove_reservation(reservation["reservation_id"])

            flash("Reservation removed succesfully", "success")
            return redirect("/")

        else:
            flash("Reservation not removed", "error")
            return redirect(url_for("reservation", reservation_id=reservation_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={}, next_page=request.referrer)

    if request.method == "POST":
        # get form information
        username = request.form["username"]
        password_1 = request.form["password_1"]
        password_2 = request.form["password_2"]
        next_page = request.form["next_page"]

        if username != username.strip():
            flash("Username must not have leading/trailing whitespace", "error")
            filled = {"username": username}
            return render_template("register.html", filled=filled, next_page=next_page)

        if password_1 != password_2:
            flash("Passwords do not match", "error")
            filled = {"username": username}
            return render_template("register.html", filled=filled, next_page=next_page)

        if len(password_1) < 8:
            flash("Password is too short", "error")
            filled = {"username": username}
            return render_template("register.html", filled=filled, next_page=next_page)

        # input validation
        if (not username or
            not password_1 or
            len(username) > 25 or
            len(username) < 5 or
            len(password_1) < 8 or
            len(password_1) > 64):
            abort(400)

        # check if the username already exists
        if usr_handler.get_users(username=username):
            flash("Username already exists", "error")
            filled = {"username": username}
            return render_template("register.html", filled=filled, next_page=next_page)

        user_id = usr_handler.create_user(username, password_1)
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        session["user_role"] = ""

        # redirect
        flash("Account created succesfully", "success")
        if next_page[-1] == "/":
            return redirect(url_for("user", username=username))
        elif next_page[-5:] == "login":
            return redirect(url_for("user", username=username))
        else:
            return redirect(next_page)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled={}, next_page=request.referrer)

    if request.method == "POST":
        # check if already logged in
        if session.get("user_id"):
            abort(400)

        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]

        user_id = usr_handler.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username

            user = usr_handler.get_user(user_id)
            session["user_role"] = user["user_role"]
            session["csrf_token"] = secrets.token_hex(16)

            flash("Login succesful", "success")
            if next_page[-1] == "/":
                return redirect(url_for("user", username=username))
            elif next_page[-8:] == "register":
                return redirect(url_for("user", username=username))
            else:
                return redirect(next_page)
        else:
            flash("Incorrect username or password", "error")
            filled = {"username": username}
            return render_template("login.html", filled=filled, next_page=next_page)

@app.route("/logout")
def logout():
    require_login()

    del session["user_id"]
    del session["user_role"]
    del session["csrf_token"]

    flash("Logout succesful", "success")
    return redirect("/")

@app.route("/search")
def search():
    # strip empty parameters
    params = {k: v for k, v in request.args.items() if v.strip()}
    if len(params) != len(request.args):
        return redirect(url_for("search", **params))

    # fuzzy text parameters
    params["title"] = f"%{params["title"]}%" if "title" in params else ""
    params["place"] = f"%{params["place"]}%" if "place" in params else ""
    params.pop("page", None)

    # pagination
    page_size = 25
    reservation_count = res_handler.reservation_count(params=params)
    page_count = math.ceil(reservation_count / page_size)
    page_count = max(page_count, 1)

    # navigation
    page = int(request.args.get("page", 1))
    page = max(1, min(page_count, page))

    # search
    reservations = res_handler.get_reservations(page=page, page_size=page_size, params=params)
    return render_template("search.html", reservations=reservations, page=page, page_count=page_count, params=params)

@app.route("/user/<username>")
def user(username):
    # get the user_id
    users = usr_handler.get_users(username=username)

    if not users:
        abort(404)
    user = users[0]

    # pagination
    page_size = 10
    reservation_count = res_handler.reservation_count(user_id=user["user_id"])
    page_count = math.ceil(reservation_count / page_size)
    page_count = max(page_count, 1)

    # navigation
    try:
        page = int(request.args.get("page", 1))
        page = max(1, min(page_count, page))
    except ValueError:
        abort(400)

    reservations = res_handler.get_reservations(user_id=user["user_id"], page=page, page_size=page_size)
    return render_template("user.html", user=user, reservations=reservations, page=page, page_count=page_count)

@app.route("/user/<username>/profile-picture")
def user_profile_picture(username):
    users = usr_handler.get_users(username=username)

    if not users:
        abort(404)
    user = users[0]

    profile_picture = usr_handler.get_profile_picture(user["user_id"])
    if not profile_picture:
        abort(404)

    response = make_response(bytes(profile_picture))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/user/<username>/change-profile-picture", methods = ["GET", "POST"])
def change_profile_picture(username):
    require_login()

    if request.method == "GET":
        users = usr_handler.get_users(username=username)
        if users:
            user = users[0]
            require_owner(user["user_id"])

        return render_template("change-profile-picture.html", user=user)

    # add profile-picture
    if request.method == "POST":
        check_csrf()

        image_file = request.files["profile-picture"]
        if not image_file:
            flash("No image file", "error")
            return redirect(url_for("change_profile_picture", username=username))

        if not image_file.filename.endswith(".jpg"):
            flash("Wrong filetype", "error")
            return redirect(url_for("change_profile_picture", username=username))

        profile_picture = image_file.read()
        if len(profile_picture) > 100 * 1024:
            flash("Image is too large", "error")
            return redirect(url_for("change_profile_picture", username=username))

        usr_handler.set_profile_picture(session.get("user_id"), profile_picture)

        flash("Profile picture added succesfully", "success")
        return redirect(url_for("user", username=username))