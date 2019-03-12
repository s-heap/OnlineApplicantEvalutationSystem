import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId
import bson

from .db import (get_connection, get_applications)
from .login import candidate_login_required

bp = Blueprint('applicationlist', __name__, url_prefix='/applicationlist')
@bp.route('/')
@candidate_login_required
def applicationlist():
    '''
    Gets the list of applications a user has from the database and renders the applicationList page with this data.

    :return: The template for the applicationlist.html page along with the lsit of application data.
    '''
    connection = get_connection()
    applications = get_applications(connection, session["user_id"])
    return render_template('applicationlist.html', applications=applications)
