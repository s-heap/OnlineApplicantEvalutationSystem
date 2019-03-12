import functools
import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import (get_connection, get_drop_down_lists, insert_cv, check_cv_made, get_candidate)
from .login import candidate_login_required
from .notifications import createNotification
from .github import get_public_contributions

bp = Blueprint("details", __name__, url_prefix="/details")

@bp.route("/", methods=("GET", "POST"))
@candidate_login_required
def details():
    '''
    If POST, calls the submit method to handle all data inputted from the form and modifies the CVData field in the candidate's document.
    If GET, the drop down data is retrieved before the cnadidate is checked to see if they have a CV already stored, If it is stored, the system loads the CV data and submits it alongside the dropdown information.

    :return: the render template for the details page with all the information needed to create the form or a redirect to the job list page after submitting the user's CV data.
    '''
    if request.method == "POST":
        return submit()

    connection = get_connection()
    drop_down_data = get_drop_down_lists(connection)

    if check_cv_made(connection, session.get('user_id')):
        CV = get_candidate(connection, session.get('user_id'))["CVData"]
        for employment in CV["Previous Employment"]:
            split_dates = employment["Length of Employment"].split()
            if len(split_dates) == 4:
                employment["Years"] = split_dates[0]
                employment["Months"] = split_dates[2]
            elif len(split_dates) == 2:
                if split_dates[1] == "month" or split_dates[1] == "months":
                    employment["Years"] = 0
                    employment["Months"] = split_dates[0]
                else:
                    employment["Years"] = split_dates[0]
                    employment["Months"] = 0
        drop_down_data["CVData"] = CV

    return render_template("details.html", dropDowns=drop_down_data)


def submit():
    '''
    Takes the data submited in the posted form and formats it into a CV dictionary which is saved in the database.

    :return: A redirect to the joblist page.
    '''
    details = dict(request.form)
    CVData = {}

    CVData["Name"] = details["name"][0]
    if "email" in details.keys():
        CVData["Email"] = details["email"][0]
    if "Github Username" in details.keys():
        CVData["Github Username"] = details["Github Username"][0]
    CVData["Degree Level"] = details["degreeLevel"][0]
    CVData["Degree Qualification"] = details["degree"][0]
    CVData["University Attended"] = details["university"][0]

    skills = []
    if "skillName[]" in details.keys():
        for name, expertise in zip(details["skillName[]"], details["skillExpertise[]"]):
            skills.append({"Skill": name, "Expertise": expertise})
        CVData["Skills"] = skills
    else:
        CVData["Skills"] = []

    employment = []
    if "company[]" in details.keys():
        for company, position, years, months in zip(details["company[]"], details["position[]"], details["jobyears[]"], details["jobmonths[]"]):
            employment.append(buildEmploymentRecord(
                company, position, years, months))

    CVData["Previous Employment"] = employment

    alevels = []
    if "aLevelName[]" in details.keys():
        for subject, grade in zip(details["aLevelName[]"], details["aLevelExpertise[]"]):
            alevels.append({"Subject": subject, "Grade": grade})
        CVData["A-Level Qualifications"] = alevels
    else:
        CVData["A-Level Qualifications"] = []

    languages = []
    if "languageName[]" in details.keys():
        for language, expertise in zip(details["languageName[]"], details["languageExpertise[]"]):
            languages.append({"Language": language, "Expertise": expertise})
        CVData["Languages Known"] = languages
    else:
        CVData["Languages Known"] = []

    if "hobbyName[]" in details.keys():
        hobbies = []
        for name, interest in zip(details["hobbyName[]"], details["hobbyExpertise[]"]):
            hobbies.append({"Name": name, "Interest": interest})
        CVData["Hobbies"] = hobbies
    else:
        CVData["Hobbies"] = []

    mongo = get_connection()
    insert_cv(mongo, session.get('user_id'), CVData)
    createNotification("success", "You CV data has been stored on the system.")
    return redirect('joblist')


def buildEmploymentRecord(company, position, years, months):
    '''
    Takes a company, position, amount of years and amount of months and formats it into a single dictionary for storing a user's CV data in the database.

    :param company: The name of the compant at a job to be stored.
    :param position: The name of the position held at a job to be stored.
    :param years: An amount of years spent at a job to be stored.
    :param months: An amount of months spent at a job to be stored.
    :return: A dictionary record of a single employment log in the valid stored format.
    '''
    record = {}
    record["Position"] = position
    record["Company"] = company
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

    record["Length of Employment"] = time
    return record
