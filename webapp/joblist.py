import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import (get_connection, get_jobs_list_general, get_jobs_list_specific)

bp = Blueprint('joblist', __name__, url_prefix='/joblist')

@bp.route('/')
def joblist():
    '''
    Loads a list of all the active jobs and if a user is logged in their applied for jobs are also loaded. This is then displayed on the joblist page.

    :return: The render template for the joblist page with data regarding the active job list.
    '''
    connection = get_connection()
    jobs = []
    if g.user:
        jobs = get_jobs_list_specific(connection, session["user_id"])
    else:
        jobs = get_jobs_list_general(connection)
    return render_template('joblist.html', jobs=jobs)
