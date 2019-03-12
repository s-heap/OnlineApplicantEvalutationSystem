import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId

from .db import get_connection
from .notifications import createNotification

bp = Blueprint("login", __name__, url_prefix="/login")

def client_login_required(view):
    '''
    Checks that a user is logged in as a client.

    :param view: The view to be passed through and displayed.
    :return: The view to load the page or a redirect if the login is not satisfied.
    '''
    return login_required(view, True)

def candidate_login_required(view):
    '''
    Checks that a user is logged in as a candidate.

    :param view: The view to be passed through and displayed.
    :return: The view to load the page or a redirect if the login is not satisfied.
    '''
    return login_required(view, False)

def login_required(view, client_flag):
    '''
    Checks that a user is logged in and is either a client or a cnadidate determined by the flag passed in. A notification is then created alongisde a redirect if not.

    :param view: The view to be passed through and displayed.
    :param client_flag: A boolean flag determining if the login required must be a client or not.
    :return: The view to load the page or a redirect if the login is not satisfied.
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            createNotification("error", "You must be logged in to view that content")
            return redirect("/login")
        elif client_flag:
            if not session.get('client_flag'):
                createNotification("error", "You must be logged in as an employee to view that content")
                return redirect("/loginClient")
        else:
            if session.get('client_flag'):
                createNotification("error", "You must be logged in as an applicant to view that content")
                return redirect("/login")
        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    '''
    Checks that a user's session is valid and if so loads in all the relevant data regarding the candidate that is needed.
    '''
    user_id = session.get('user_id')
    connection = get_connection()
    if user_id is None:
        g.user = None
    else:
        client_flag = session.get('client_flag')
        if client_flag:
            g.user = user = connection.Employee.find_one({"_id": ObjectId(user_id)})
        else:
            g.user = user = connection.Candidate.find_one(
                {"_id": ObjectId(user_id)})

@bp.route("/", methods=("GET", "POST"))
def auth():
    '''
    If POST, the form is checked to see if it is a login or a register and the appropriate method is called.
    If GET, the login.html page is simply displayed.

    :return: A redirect depending on the success of a login or the login page.
    '''
    if request.method == "POST":
        if request.form["in/up"] == "in":
            login()
        elif request.form["in/up"] == "up":
            register()
        if "user_id" in session.keys():
            return redirect("details")
    return render_template("login.html")

def login():
    """
    Log in a registered user by adding the user id to the session.
    """
    connection = get_connection()
    username = request.form["username"]
    password = request.form["password"]
    user = connection.Candidate.find_one({"Username": username})
    error = False
    if user is None:
        createNotification("error", "Incorrect username")
        error = True
    elif not check_password_hash(user["Password"], password):
        createNotification("error", "Incorrect password")
        error = True

    if not error:
        create_session(user, False)

def register():
    """
    Registered a user and log them in by adding their user id to the session.
    """
    connection = get_connection()
    username = request.form["username"]
    password = request.form["password"]
    error = False
    if username == "":
        createNotification("error", "Username is required.")
        error = True
    if password == "":
        createNotification("error", "Password is required.")
        error = True
    if connection.Candidate.find_one({"Username": username}):
        createNotification(
            "error", "User {0} is already registered.".format(username))
        error = True

    if not error:
        connection.Candidate.insert_one(
            {"Username": username, "Password": generate_password_hash(password)})
        create_session(
            connection.Candidate.find_one({"Username": username}), False)

def create_session(user, client_flag):
    '''
    Creates a session for the user with their id and a flag determining if they are a client or a candidate.

    :param user: All the data regarding the user logging in.
    :param client_flag: A boolean flag indicating if the user is a client or candidate.
    '''
    session.clear()
    session["user_id"] = str(user["_id"])
    session["client_flag"] = client_flag
    createNotification(
        "success", "You are now logged in as {0}".format(user["Username"]))

@bp.route("/logout")
def logout():
    """
    Clear the current session, including the stored user id.
    """
    session.clear()
    return redirect(url_for("home.home"))
