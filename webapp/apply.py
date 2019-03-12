import functools
import itertools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from bson import ObjectId

from .db import (get_connection, check_already_applied, get_test_questions, check_correct_answer, create_application, check_cv_made, get_community_contributions)
from .login import candidate_login_required
from .notifications import createNotification

bp = Blueprint('apply', __name__, url_prefix='/apply')
@bp.route('/')
@candidate_login_required
def apply():
    '''
    Checks that the job being selected to apply to is valid, that te candidate applying has a CV stored and that they haven't already applied for that job before retrieving all valid test questions for the job and rendering the page.

    :return: The apply page with the correct test questions or a redirect if the user should not be able to load the page.
    '''
    if request.method == "GET":
        job_id = request.args.get("id")
        name = request.args.get("name")
        if job_id:
            candidate_id = session.get('user_id')
            if candidate_id:
                connection = get_connection()
                if check_cv_made(connection, candidate_id):
                    if not check_already_applied(connection, job_id, candidate_id):
                        questions = get_test_questions(connection, job_id)
                        return render_template('apply.html', questions=questions)
                    else:
                        createNotification(
                            "error", "You have already applied for that job.")
                        return redirect("joblist")
                else:
                    createNotification("error", "You must first create a CV")
                    return redirect("details")
        else:
            createNotification("error", "You cannot apply for an invalid job.")
            return redirect("joblist")
    return redirect('joblist')


@bp.route('/submit', methods=["POST"])
@candidate_login_required
def submit():
    '''
    Compiles the question data submitted by the form and checks each answer before storing the candidates results by creating a document for their application in the Application collection in the database.

    :return: A redirect to the coding test page to test the candidate on their technical skills.
    '''
    data = dict(request.form)

    job_id = data["Job ID"][0]
    connection = get_connection()

    numeracy_answers = []
    for x in range(1, (len(data["NumeracyID[]"]) + 1)):
        string = "NumeracyAnswer[]" + str(x)
        numeracy_answers.append(data[string][0])

    numeracy_score = 0
    for answer, id in zip(numeracy_answers, data["NumeracyID[]"]):
        if check_correct_answer(connection, id, answer):
            numeracy_score += 1
    numeracy_score = 100 * numeracy_score / len(data["NumeracyID[]"])

    literacy_answers = []
    for x in range(1, (len(data["LiteracyID[]"]) + 1)):
        string = "LiteracyAnswer[]" + str(x)
        literacy_answers.append(data[string][0])

    literacy_score = 0
    for answer, id in zip(literacy_answers, data["LiteracyID[]"]):
        if check_correct_answer(connection, id, answer):
            literacy_score += 1
    literacy_score = 100 * literacy_score / len(data["LiteracyID[]"])

    application = {}

    application["Candidate ID"] = ObjectId(session.get('user_id'))
    community_contributions = get_community_contributions(
        connection, application["Candidate ID"])
    if community_contributions > 10:
        community_contributions = 100
    else:
        community_contributions = 0

    application["Test Results"] = {"Literacy": literacy_score, "Numeracy": numeracy_score, "Abstract Reasoning": 0, "Technical": 0, "Community Contribution": community_contributions}

    application["Job ID"] = ObjectId(job_id)

    application_id = create_application(connection, application)
    return redirect(url_for('codingtest.codingtest', id=application_id))
