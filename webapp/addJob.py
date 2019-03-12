import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from datetime import datetime
from bson import ObjectId
import sys
sys.path.insert(0, 'machinelearning/')

from .db import (get_connection, get_drop_down_lists, is_job_already_created, create_job, get_job_by_name)
from .login import client_login_required
from .notifications import createNotification
import mlmodeltrainer as tm

bp = Blueprint("addJob", __name__, url_prefix="/addJob")

@bp.route("/", methods=("GET", "POST"))
@client_login_required
def addJob():
    '''
    if POST, takes all the data submitted in the form and stores it in the system with the submit method.
    if GET, retrieves the dictionary of field values and renders the addJob.html page with this data.

    :return: The render template for the addExistingJob.html page or a redirect to the clientJobs page.
    '''
    if request.method == "POST":
        return submit()
    connection = get_connection()
    dropDownData = get_drop_down_lists(connection)

    return render_template("addJob.html", dropDowns=dropDownData)

def submit():
    '''
    Retrieves all the data from the posted form to create a full document to be stored by the in the Job collection. Additionally the machine learning model stored with the job's name is created and trained.

    :return: A redirect to the clientJobs page.
    '''
    connection = get_connection()
    job_details = dict(request.form)
    job_data = {}

    if is_job_already_created(connection, job_details["title"][0]):
        createNotification("error", "A job with that name has already been created.")
        return redirect("addExistingJob")

    job_data["Job Name"] = job_details["title"][0]

    job_data["Job Description"] = job_details["description"][0]

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

    model_cv = {}

    if "university[]" in job_details.keys():
        model_cv["Approved Universities"] = job_details["university[]"]
    else:
        model_cv["Approved Universities"] = []

    if "level" in job_details.keys():
        model_cv["Degree Level"] = job_details["level"][0]
    else:
        model_cv["Degree Level"] = []

    if "degree[]" in job_details.keys():
        model_cv["Approved Degree"] = job_details["degree[]"]
    else:
        model_cv["Approved Degree"] = []

    if "positionName[]" in job_details.keys():
        position_list = []
        for position, years, months in zip(job_details["positionName[]"], job_details["positionYear[]"], job_details["positionMonth[]"]):
            position_list.append({"Position": position, "Length of Employment": getEmploymentLength(years, months)})
        model_cv["Previous Employment"] = position_list
    else:
        model_cv["Previous Employment"] = []

    if "skillName[]" in job_details.keys():
        skill_list = []
        for name, expertise in zip(job_details["skillName[]"], job_details["skillExpertise[]"]):
            skill_list.append({"Skill": name, "Expertise": expertise})
        model_cv["Skills"] = skill_list
    else:
        model_cv["Skills"] = []

    if "language[]" in job_details.keys():
        language_list = []
        for language, expertise in zip(job_details["language[]"], job_details["languageExpertise[]"]):
            language_list.append({"Language": language, "Expertise": expertise})
        model_cv["Languages Known"] = language_list
    else:
        model_cv["Languages Known"] = []

    if "aLevelName[]" in job_details.keys():
        aLevel_list = []
        for subject, grade in zip(job_details["aLevelName[]"], job_details["aLevelExpertise[]"]):
            aLevel_list.append({"Subject": subject, "Grade": grade})
        model_cv["A-Level Qualifications"] = aLevel_list
    else:
        model_cv["A-Level Qualifications"] = []

    job_data["Model CV"] = model_cv

    connection = get_connection()
    create_job(connection, job_data)

    create_model(job_data["Model CV"], job_data["Job Name"].replace(" ", ""))

    createNotification("success", "Your job has been successfully created")
    return redirect('clientJobs')

def create_model(exemplar_cv, model_name):
    '''
    Takes the name of the machine learning model and the model CV, then creates and trains the model.

    :param exemplar_cv: The dictionary containg the model CV used to create the machine learning model.
    :param model_name: The name of the machine loading model use to find it's stored file.
    '''
    print("************************NEW RUN************************")
    mlObj = tm.MLModelTrainer(50000)
    mlObj.setExemplarCV(exemplar_cv)
    print("*******************DICTIONARY CREATED******************")
    print("***********************DATA LOADED*********************")

    _X_train, Y_train, _X_test, Y_test = mlObj.split_data(0, 50000)
    print("***********************DATA SPLIT**********************")
    X_train = mlObj.scale_data(_X_train)
    X_test = mlObj.scale_data(_X_test)
    print("***********************DATA SCALED*********************")

    mlObj.fit(X_train, Y_train)
    print("***********************DATA TRAINED********************")
    mlObj.test(X_test, Y_test)
    print("***********************DATA TESTED*********************")
    data=mlObj.getDataset()

    mlObj.saveModel(model_name, "machinelearning/models/"+model_name+"/")
    mlObj.saveModelData(model_name, "machinelearning/models/"+model_name+"/", _X_train, _X_test, Y_train, Y_test)
    print("***********************DATA SAVED**********************")

def getEmploymentLength(years, months):
    '''
    Takes two integers years and months and creates a string displaying the years and months.

    :param years: An integer amount of years spent at a job.
    :param months: An integer amount of months spent at a job.
    :return: A string depicting the time spent employed in years and months.
    '''
    time = ""
    if int(years) > 0:
        if int(years) == 1:
            time += str(years) + " year"
        else:
            time += str(years) + " years"
    if int(months) > 0:
        if time:
            time += " "
        if int(months) == 1:
            time += str(months) + " month"
        else:
            time += str(months) + " months"

    return time
