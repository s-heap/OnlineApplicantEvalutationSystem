import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import (get_connection, get_application)
from .login import candidate_login_required
from .notifications import createNotification

bp = Blueprint('applicationview', __name__, url_prefix='/applicationview')
@bp.route('/')
@candidate_login_required
def applicationview():
    '''
    Acquires the application data for a specific application passed in as the ID before displaying the applicationview page unless the application does not below to the user logged in. Then a redirect is made to the joblist page.

    :return: A redirect to the joblist page or the applicationview.html page with data acout the specific application.
    '''
    if request.method == "GET":
        application_id = request.args.get("id")
        if application_id:
            connection = get_connection()
            application_data = get_application(connection, application_id, session["user_id"])

            if application_data:
                return render_template('applicationview.html', applicationData=application_data)

    createNotification("error", "Only your applications can be viewed.")
    return redirect("applicationlist")
