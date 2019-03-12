import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId

from .db import get_connection
from .notifications import createNotification
from .login import create_session

bp = Blueprint("loginClient", __name__, url_prefix="/loginClient")


@bp.route("/", methods=("GET", "POST"))
def login():
    '''
    Logs a client in by processing their login form.
    '''
    if request.method == "POST":
        connection = get_connection()
        username = request.form["username"]
        password = request.form["password"]
        user = connection.Employee.find_one({"Username": username})
        print("User: " + str(user))
        error = False
        if user is None:
            createNotification("error", "Incorrect username")
            error = True
        elif not check_password_hash(user["Password"], password):
            createNotification("error", "Incorrect password")
            error = True

        if not error:
            create_session(user, True)
            return redirect("clientJobs")
    return render_template("loginClient.html")
