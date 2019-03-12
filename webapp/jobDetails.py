import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import (get_connection, get_job, create_job_shortlist, get_candidate, get_applied_number, set_job_completed, reinforce_model)
from .login import client_login_required

bp = Blueprint('jobDetails', __name__, url_prefix='/jobDetails')

@bp.route('/', methods=("GET", "POST"))
@client_login_required
def jobDetails():
    '''
    If POST, a sjortlist for the job in question is created before the page is loaded.
    If GET, The jobDetails page is loaded. If the job application period has expired and it has no stored shortlist it will be created before loading.

    :return: The jobDetails page with all relevant information to display properly.
    '''
    connection = get_connection()

    if request.method == 'POST':
        create_job_shortlist(connection, request.args.get("id"))

    job = get_job(connection, request.args.get("id"))

    if "Closed" in job.keys():
        if "Latest Shortlist" not in job.keys() or len(job["Latest Shortlist"]) < int(job["Applicants Required"]):
            create_job_shortlist(connection, request.args.get("id"))
            job = get_job(connection, request.args.get("id"))

    if "Latest Shortlist" in job.keys():
        candidate_data = []
        for cid in job["Latest Shortlist"]:
            candidate_data.append(get_candidate(connection, cid))
        job["Latest Shortlist"] = candidate_data
    job["Application Count"] = get_applied_number(connection, request.args.get("id"))
    return render_template('jobDetails.html', job=job)

@bp.route('/feedback', methods=("GET", "POST"))
@client_login_required
def feedback():
    '''
    Loads the feedback data submited in the sent form, this is then used to reinforce the machine leraning model before the job is modified to be set to closed in the database.

    :return: A redirect to the clientJobs page after submitting the feedback data to reinforce the ML model.
    '''
    connection = get_connection()
    feedback_details = dict(request.form)

    if "classification[]" in feedback_details.keys():
        reinforce_model(connection, feedback_details["jobName"][0].replace(" ", ""), feedback_details["classification[]"], feedback_details["candidateID[]"])

    set_job_completed(connection, feedback_details["jobID"][0])

    return redirect("clientJobs")
