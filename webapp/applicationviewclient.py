import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import (get_connection, check_already_applied)
from .login import client_login_required
from .notifications import createNotification

bp = Blueprint('applicationviewclient', __name__, url_prefix='/applicationviewclient')
@bp.route('/')
@client_login_required
def applicationviewclient():
    '''
    Acquires the application data for a specific application from both a candidate id and a job id applicationviewclient page unless the application does not below to the user logged in. Then a redirect is made to the jobDetails page.

    :return: A redirect to the jobDetails page or the applicationview.html page with data regarding the specific application.
    '''
    if request.method == "GET":
        job_id = request.args.get("jid")
        candidate_id = request.args.get("cid")
        if job_id:
            if candidate_id:
                connection = get_connection()
                application_data = check_already_applied(connection, job_id, candidate_id)
                if application_data:
                    return render_template('applicationviewclient.html', applicationData=get_radar_data(application_data))

    createNotification("error", "Only your applications belonging to your job can be viewed.")
    return redirect(url_for("jobDetails.jobDetails", id=request.args.get("jid")))

def get_radar_data(application_data):
    c_languages = []
    c_scores = {}
    j_languages = []
    j_Scores = {}
    for language in application_data["Candidate"]["CVData"]["Languages Known"]:
        c_languages.append(language["Language"])
        c_scores[language["Language"]] = language["Expertise"]

    for language in application_data["Job"]["Model CV"]["Languages Known"]:
        j_languages.append(language["Language"])
        j_Scores[language["Language"]] = language["Expertise"]

    total_languages = list(set().union(c_languages, j_languages))
    candidate_languages = []
    for c in total_languages:
        if c not in c_languages:
            candidate_languages.append(0)
        else:
            candidate_languages.append(int(c_scores[c]))

    job_languages = []
    for j in total_languages:
        if j not in j_languages:
            job_languages.append(0)
        else:
            job_languages.append(int(j_Scores[j]))


    application_data["Radar"] = {"Languages Known": {"Keys" : total_languages, "Candidate Languages": candidate_languages, "Job Languages": job_languages}}
    print("\n\n\n")
    print(total_languages)
    print(candidate_languages)
    print(job_languages)
    print("\n\n\n")
    return application_data
