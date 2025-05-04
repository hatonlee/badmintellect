import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort, make_response
import res_handler, usr_handler, tag_handler, com_handler, config
import math

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

# main page
@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    # pagination
    page_size = 25
    reservation_count = res_handler.count()
    page_count = math.ceil(reservation_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    
    if page > page_count:
        return redirect(f"/{page_count}")

    reservations = res_handler.get_reservations(page=page, page_size=page_size)
    return render_template("index.html", page=page, page_count=page_count, reservations=reservations)

# show a reservation
@app.route("/reservation/<int:reservation_id>", methods=["GET", "POST"])
def show_reservation(reservation_id):
    reservation = res_handler.get_reservations(r_id=reservation_id)[0]

    if not reservation:
        abort(404)

    # show the reservation page
    if request.method == "GET":
        tags = tag_handler.get_tags(reservation_id)
        comments = com_handler.get_comments(reservation_id)
        return render_template("reservation.html", reservation=reservation, tags=tags, comments=comments)

    # add a comment to the reservation
    if request.method == "POST":
        # get form information
        comment = request.form["comment"]

        # input validation
        if not comment or len(comment) > 1000:
            abort(403)

        # create the comment
        try:
            comment_id = com_handler.add_comment(comment, reservation_id)
        except sqlite3.IntegrityError:
            abort(403)

        return redirect(f"/reservation/{reservation_id}")

# new reservation
@app.route("/new-reservation", methods=["GET", "POST"])
def new_reservation():
    require_login()

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

        # input validation
        if (not title or
            not start_time or
            not end_time or
            not place or
            len(title) > 50 or
            len(start_time) > 25 or
            len(end_time) > 25 or
            len(place) > 50):
            abort(403)

        # create the reservation
        reservation_id = res_handler.add_reservation(title, start_time, end_time, place, user_id)
        
        # add tags
        for tag in tags:
            tag_handler.add_tag(tag, reservation_id)
        
        # redirect to the reservation
        return redirect(f"/reservation/{reservation_id}")

# edit reservation
@app.route("/edit/<int:reservation_id>", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    require_login()

    reservation = res_handler.get_reservations(r_id=reservation_id)[0]

    # check permission
    if reservation["user_id"] != session["user_id"]:
        abort(403)

    # show the edit page
    if request.method == "GET":
        allowed_tags = tag_handler.get_allowed()
        tags = tag_handler.get_tags(reservation_id)
        return render_template("edit.html", reservation=reservation, allowed_tags=allowed_tags, tags=tags)

    # commit the edit
    if request.method == "POST":
        # get form information
        new_title = request.form["title"]
        new_start_time = request.form["start_time"]
        new_end_time = request.form["end_time"]
        new_place = request.form["place"]
        tags = request.form.getlist("tag")

        # input validation
        if (not new_title or
            not new_start_time or
            not new_end_time or
            not new_place or
            len(new_title) > 50 or
            len(new_start_time) > 25 or
            len(new_end_time) > 25 or
            len(new_place) > 50):
            abort(403)

        # remove old tags and add new
        tag_handler.remove_tag("%", reservation_id)
        for tag in tags:
            tag_handler.add_tag(tag, reservation_id)

        # update the reservation
        res_handler.update_reservation(reservation_id, new_title, new_start_time, new_end_time, new_place)
        
        # redirect to the reservation
        return redirect(f"/reservation/{reservation_id}")

# remove reservation
@app.route("/remove/<int:reservation_id>", methods=["GET", "POST"])
def remove_reservation(reservation_id):
    require_login()

    reservation = res_handler.get_reservations(r_id=reservation_id)[0]

    # check permission
    if reservation["user_id"] != session["user_id"]:
        abort(403)

    # show the remove page
    if request.method == "GET":
        return render_template("remove.html", reservation=reservation)

    # commit the removal
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

        # input validation
        if (not username or
            not password_1 or
            len(username) > 25):
            abort(403)

        # check if the username already exists
        if usr_handler.get_users(u_username=username):
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
    require_login()
    del session["user_id"]
    return redirect("/")

# search
@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    query_match_all = f"%{query}%"
    reservations = res_handler.get_reservations(r_title=query_match_all)
    return render_template("search.html", query=query, reservations=reservations)

# user page
@app.route("/user/<username>")
def user(username):
    # get the user_id
    users = usr_handler.get_users(u_username=username)
    
    if not users:
        abort(403)
    user = users[0]

    # get reservations of the user
    reservations = res_handler.get_reservations(r_user_id=user[0])

    return render_template("user.html", user=user, reservations=reservations)

# user profile picture page
@app.route("/user/<username>/image")
def user_image(username):
    users = usr_handler.get_users(u_username=username)

    if not users:
        abort(403)
    user = users[0]

    image = usr_handler.get_image(user[0])
    if not image:
        abort(404)
    
    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

# add profile picture
@app.route("/add-image", methods = ["GET", "POST"])
def add_image():
    require_login()

    # show the form
    if request.method == "GET":
        return render_template("add-image.html")
    
    # add the image
    if request.method == "POST":
        image_file = request.files["image"]
        if not image_file.filename.endswith(".jpg"):
            return "Incorrect filetype"
        
        image = image_file.read()
        if len(image) > 100 * 1024:
            return "Filesize too large"
    
        user_id = session["user_id"]
        usr_handler.set_image(user_id, image)

        username = usr_handler.get_users(u_id=user_id)[0]["username"]
        
        return redirect(f"/user/{username}")