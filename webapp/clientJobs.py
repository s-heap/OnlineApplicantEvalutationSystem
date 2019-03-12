import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import (get_connection, get_client_job_list)
from .login import client_login_required

bp = Blueprint('clientJobs', __name__, url_prefix='/clientJobs')
@bp.route('/')
@client_login_required
def clientJobs():
    '''
    Gets the list of jobs the logged in client has created then displayes the clientJobs.html page.

    :return: The render template for the clientJobs.html page alongisde data about the jobs the client has created,
    '''
    connection = get_connection()
    job_data = get_client_job_list(connection, session.get('user_id'))
    return render_template('clientJobs.html', jobData=job_data)
