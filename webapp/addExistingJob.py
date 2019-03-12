import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from datetime import datetime
from bson import ObjectId
import sys
sys.path.insert(0, 'machinelearning/')

from .db import (get_connection, get_drop_down_lists, create_job, get_job_by_name, get_job_names)
from .login import client_login_required
from .notifications import createNotification
import reinforcedmodel as rm

bp = Blueprint("addExistingJob", __name__, url_prefix="/addExistingJob")

@bp.route("/", methods=("GET", "POST"))
@client_login_required
def addExistingJob():
    '''
    If POST, the new job data is stored in the database using the submit methodself.
    If GET, the get_drop_down_lists method is used to get drop down data, additionally the existing job names are retrieved and added before the page is loaded with this data.

    :return: The render template for the addExistingJob.html page or a redirect to the clientJobs page.
    '''
    if request.method == "POST":
        return submit()
    connection = get_connection()
    drop_down_data = get_drop_down_lists(connection)
    drop_down_data["Existing Jobs"] = get_job_names(connection)

    return render_template("addExistingJob.html", dropDowns=drop_down_data)

def submit():
    '''
    Retrieves all the data from the posted form, then combines it with the model CV data from the existing job with the name specified to create a full document to be stored by the in the Job collection. Additionally the machine learning model stored with the job's name is retrained.

    :return: A redirect to the clientJobs page.
    '''
    connection = get_connection()
    job_details = dict(request.form)

    existing_job_data = get_job_by_name(connection, job_details["title"][0])
    job_data = {}

    job_data["Job Name"] = existing_job_data["Job Name"]

    job_data["Job Description"] = existing_job_data["Job Description"]

    job_data["Employee ID"] = ObjectId(job_details["employeeID"][0])

    job_data["Applicants Required"] = job_details["applicantNo"][0]

    availability = {}
    availability["Date Created"] = datetime.strptime(job_details["created"][0], "%Y-%m-%d")
    availability["End Date"] = datetime.strptime(job_details["end"][0], "%Y-%m-%d")
    job_data["Availability"] = availability

    question_difficulty = {}
    question_difficulty["Literacy"] = job_details["literacy"][0]
    question_difficulty["Numeracy"] = job_details["numeracy"][0]
    question_difficulty["Abstract Reasoning"] = job_details["abstractReasoning"][0]
    question_difficulty["Situational Awareness"] = job_details["situationalJudgement"][0]
    job_data["Question Difficulty"] = question_difficulty

    job_data["Model CV"] = existing_job_data["Model CV"]

    create_job(connection, job_data)

    create_reinforced_model(job_data["Job Name"].replace(" ", ""))

    createNotification("success", "Your job has been successfully created")
    return redirect('clientJobs')

def create_reinforced_model(model_name):
    '''
    Takes the name of the machine learning model, then laods in the model, retrains th emodel now with any new fed back data then saves the model.

    :param model_name: The name of the machine loading model use to find it's stored file.
    '''
    print("************************NEW RUN************************")
    ml_object = rm.ReinforcedModel(model_name, "machinelearning/models/")
    print("*****************REINFORCED MODEL LOADED***************")
    ml_object.fit()
    print("*************************DATA FIT**********************")
    ml_object.saveModelData()
    print("***********************DATA SAVED**********************")
