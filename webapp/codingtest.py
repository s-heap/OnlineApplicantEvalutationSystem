import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
import json
import sys
sys.path.insert(0, "candidateCodeTesting/tests")

from .db import (get_connection, get_random_question, update_technical_score, get_application)
from .login import candidate_login_required
from .notifications import createNotification

import duplicatenumber_test as dt
import permutation_test as pt
bp = Blueprint('codingtest', __name__, url_prefix='/codingtest')

@bp.route('/', methods=("GET", "POST"))
@candidate_login_required
def codingtest():
    f = []
    q = get_question()
    if request.method == "POST":
        run_code()
        f = get_feedback(q["Question Name"])
        # print("\n\n\n\nYEET\n\n\n\n")
        # print(f)
        # return render_template('codingtest.html', question=q, feedback=json.dumps(f))
    return render_template('codingtest.html', question=q, feedback=json.dumps(f))


@bp.route('/submit', methods=("GET", "POST"))
def submit_code():
    connection = get_connection()
    q = get_question()
    applicationID=request.args.get("id")
    applicationData=get_application(connection, applicationID, session['user_id'])
    run_code()
    update_technical_score(connection, applicationData, get_technical_score(q["Question Name"]))
    createNotification("success", "Application sent!")
    return redirect(url_for('applicationview.applicationview', id=applicationID))

@bp.route('/run', methods=("GET", "POST"))
def run():
    run_code()
    q = get_question()
    f = get_feedback(q["Question Name"])
    return jsonify(result=f)


def run_code():
    try:
        f = open("candidateCodeTesting/test_codingTest.py","w+")
        details = dict(request.form)
        if 'preview-form-comment' in details.keys():
            code = details['preview-form-comment']
            for line in code:
                print(line)
                f.write(line)
        f.close()
    except:
        print("\n\n\nFILE DIDNT OPEN\n\n\n")

def get_question():
    mongo = get_connection()
    return get_random_question(mongo, "Technical")

def get_feedback(question):
    if "1. Permutations" == question:
        return pt.run_tests_candidate()
    elif "2. Find the Duplicate Number" == question:
        return dt.run_tests_candidate()

def get_technical_score(question):
    if "1. Permutations" == question:
        test_results = pt.run_tests()
    elif "2. Find the Duplicate Number" == question:
        test_results = dt.run_tests()
    score = 0
    for i in test_results:
        if i == True:
            score = score + 20
    return score
