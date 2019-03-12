import click
import random
import requests
from flask import (Flask, current_app, g)
from flask.cli import with_appcontext
from flask_pymongo import PyMongo
from bson import ObjectId
from statistics import mean
from datetime import datetime
import sys
sys.path.insert(0, "machinelearning/")

from .github import get_public_contributions
import mlmodel as ml
import reinforcedmodel as rm

'''
A list of all the fields stored in the input_fields collection
'''
input_fields = ["University Attended", "Degree Qualification", "Hobbies",
               "Previous Employment Position", "A-Level Qualifications", "Languages Known", "Skills", "Degree Level"]

def get_connection():
    '''
    Creates and returns a MongoDB connectiong with the database

    :return: A connection ot the mongo database
    '''
    app = Flask(__name__)
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/SeeVDB'
    mongo = PyMongo(app)
    return mongo.db

# Takes a mongoDB connectino and a field name and returns every stored value for that field.
def get_field_list(connection, field):
    '''
    Returns all the values that the system has stored for a specific field (e.g. "University Attended" or "Skill")

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param field: The name of the field to find the stored values for.
    :return: A list of different possible values for the entered field.
    '''
    if field not in input_fields:
        return False
    query = list(connection.InputFields.find( {"Field": field}, {"Value": 1, "_id": 0} ).sort("Value") )
    output = []
    for document in query:
        output.append(document["Value"])
    return output

def get_drop_down_lists(connection):
    '''
    Returns all the values that the system has stored for a all fields (e.g. "University Attended" or "Skill")

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :return: A dictionary containing all the stored valuess for each input field.
    '''
    output = {}
    for field in input_fields:
        output[field] = get_field_list(connection, field)
    return output

def get_candidate(connection, candidate_id):
    '''
    Returns the candidate document given an ID and a connection to the database.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidate_id: The ID of the candidate in question.
    :return: A dictionary containing the entire candidate document from the database.
    '''
    return connection.Candidate.find_one( {"_id": ObjectId(candidate_id)} )

def get_applications(connection, candidate_id):
    '''
    Gets the list of all applications tied to the candidate ID and categorises them into into "Active", "Inactive" and "Completed".

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidate_id: The ID of the candidate in question.
    :return: A dictionary containing all applications attached to the candidate ID passed in seperated into "Active", "Inactive" and "Completed"
    '''
    applications_list = list(connection.Application.find( {"Candidate ID": ObjectId(candidate_id)} ))
    return categorise_applications(connection, applications_list)


def categorise_applications(connection, applications_list):
    '''
    Takes a list of applicaitons and categorises them into into "Active", "Inactive" and "Completed" whilst adding the job data for the application in question.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param applications_list: A list of applications to categorise.
    :return: A dictionary containing all applications in the passed in application list seperated into "Active", "Inactive" and "Completed"
    '''
    current_time = datetime.utcnow()
    active_applications = []
    inactive_applications = []
    complete_inactive_jobs = []
    for application in applications_list:
        application["Job Data"] = connection.Job.find_one( {"_id": application["Job ID"]} )
        if current_time > application["Job Data"]["Availability"]["End Date"]:
            if "Closed" in applicaiton["Job Data"].keys():
                complete_inactive_jobs.append(application)
            else:
                inactive_applications.append(application)
        else:
            active_applications.append(application)
    return {"Active": active_applications, "Inactive": inactive_applications, "Completed": complete_inactive_jobs}

def get_jobs_list_general(connection):
    '''
    Gets all job documents which haven't closed yet.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :return: The list of all active jobs.
    '''
    current_time = datetime.utcnow()
    return list(connection.Job.find( {"Availability.End Date": {"$gte": current_time}} ))


def get_jobs_list_specific(connection, candidate_id):
    '''
    Gets all job documents which haven't closed yet aswell as the application information for those therein which are applied to by the candidate ID passed in.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidate_id: The ID of the candidate in question.
    :return: The list of all active jobs alongside whether the candiate in question has applied to them.
    '''
    output = get_jobs_list_general(connection)
    for job in output:
        application = connection.Application.find_one(
            {"Job ID": ObjectId(job["_id"]), "Candidate ID": ObjectId(candidate_id)} )
        if application:
            job['Application'] = application["_id"]
    return output

def get_client_job_list(connection, employee_id):
    '''
    Finds all the jobs created by a specific employee and categorises them into "Active", "Inactive" and "Completed".

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param employee_id: The ID of the employee in question.
    :return: A dictionary containing all jobs created by the employee in question seperated into "Active", "Inactive" and "Completed"
    '''
    current_time = datetime.utcnow()
    active_jobs = list(connection.Job.find( {"Employee ID":ObjectId(employee_id), "Availability.End Date": {"$gte": current_time}} ))
    inactive_jobs = list(connection.Job.find( {"Employee ID":ObjectId(employee_id), "Availability.End Date": {"$lt": current_time}} ))
    non_completed_inactive_jobs = []
    completed_inactive_jobs = []
    for job in inactive_jobs:
        if "Completed" not in job.keys():
            non_completed_inactive_jobs.append(job)
        else:
            completed_inactive_jobs.append(job)
    return {"Active": active_jobs, "Inactive": non_completed_inactive_jobs, "Completed": completed_inactive_jobs}

def get_application(connection, application_id, candidate_id):
    '''
    Checks if the application in question is attributed to the correct user and appends the information of the job it is for.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param application_id: The ID of the application in question.
    :param candidate_id: The ID of the candidate in question.
    :return: A dictionary containing a single application document with the new field 'Job' conatining all of it's job data.
    '''
    application = connection.Application.find_one( {"_id": ObjectId(application_id), "Candidate ID": ObjectId(candidate_id)} )
    if application:
        job = connection.Job.find_one( {"_id": ObjectId(application["Job ID"])} )
        if job:
            application['Job'] = job
            return application
    return False

def get_random_question(connection, question_type):
    '''
    Finds a random stored question of the type passed in.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param question_type: The type of question to be retrieved. (e.g. Literacy, Numeracy, Technical)
    :return: A dictionary containing a the document for the question.
    '''
    output = list(connection.TestQuestions.find( {"Question Type": question_type} ))
    return random.choice(output)

def check_already_applied(connection, job_id, candidate_id):
    '''
    Checks if there exists an application connecting a job and a candidate.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_id: The ID of the job in question.
    :param candidate_id: The ID of the candidate in question.
    :return: A boolean value dictating if there is an application with the passed in job ID and candidate ID.
    '''
    application = connection.Application.find_one( {"Job ID": ObjectId(job_id), "Candidate ID": ObjectId(candidate_id)} )
    if application:
        job = connection.Job.find_one( {"_id": ObjectId(application["Job ID"])} )
        if job:
            application['Job'] = job
        candidate = connection.Candidate.find_one( {"_id": ObjectId(application["Candidate ID"])} )
        if candidate:
            application['Candidate'] = candidate
        return application
    return False

def get_question_list(connection, question_type, question_difficulty):
    '''
    Returns the list of questions with a specified difficulty and type.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param question_type: The type of question to be retrieved. (e.g. Literacy, Numeracy, Technical)
    :param question_difficulty: The difficulty of the questions to be retrieved.
    :return: A list of all the question documents of the specified type and difficulty.
    '''
    question_list = list(connection.TestQuestions.find( {"Question Type": question_type, "Question Difficulty": str(question_difficulty)} ))
    if question_list:
        return question_list
    return False

def filter_question_list(questions_list):
    '''
    Takes a list of questions and randomly selects 4, these are then formatted to so the correct and incorrect answers cannot be distinguished.

    :param questions_list: A list of questions to be filtered for.
    :return: A list of 4 chosen, formatted questions.
    '''
    selected_questions = []
    for x in range(0, 4):
        selected_questions.append(questions_list.pop(random.randint(0, (len(questions_list)-1))))
    return format_test_questions(selected_questions)

def format_test_questions(questions_list):
    '''
    Takes a list of questions and returns a list of those same questions where the correct and incorrect answers are mixed.

    :param questions_list: A list of questions to be formatted.
    :return: A list of formatted questions.
    '''
    formatted_questions = []
    for question in questions_list:
        filtered = {}
        filtered["Question Text"] = question["Question Text"]
        answers = question["Incorrect Answers"]
        answers.insert(random.randint(0, (len(answers)-1)),
                       question["Correct Answer"])
        filtered["Answers"] = answers
        filtered["_id"] = question["_id"]
        formatted_questions.append(filtered)
    return formatted_questions

def get_test_questions(connection, job_id):
    '''
    Takes a job ID and selects the question difficulties it requires, it then finds 4 randomly selected questions from each and formats them so the correct and incorrect answers are mixed.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_id: The ID of the job in question.
    :return: A dicitonary containing lists of questions for each type.
    '''
    job = connection.Job.find_one( {"_id": ObjectId(job_id)} )
    output = {}
    if job:
        numeracy = get_question_list(connection, "Numeracy", job["Question Difficulty"]["Numeracy"])
        literacy = get_question_list(connection, "Literacy", job["Question Difficulty"]["Literacy"])
        if numeracy:
            if literacy:
                output["Numeracy"] = filter_question_list(numeracy)
                output["Literacy"] = filter_question_list(literacy)
                return output
    return False

def check_correct_answer(connection, question_id, answer):
    '''
    Takes a question ID and an answer and returns a boolean value depending on if the answer passed in was correct.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param question_id: The ID of the question to be checked.
    :return: A boolean value determining if the answer was correct or incorrect.
    '''
    query = connection.TestQuestions.find_one( {"_id": ObjectId(question_id)}, {"Correct Answer": 1} )
    if answer == query["Correct Answer"]:
        return True
    return False

def create_application(connection, document):
    '''
    Takes a document and stores it as a new application file. False is then returned if it fails and the new ID is returned if it succeeds.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param document: The document dictionary to be stored in the Application collection.
    :return: The ID of the application created.
    '''
    connection.Application.insert_one(document)
    application = connection.Application.find_one( {"Job ID": ObjectId(document["Job ID"]), "Candidate ID": ObjectId(document["Candidate ID"])} )
    if application:
        return application["_id"]
    return False

def update_technical_score(connection, document, score):
    '''
    Takes a document and a score, then using the document's ID it sets the Application's Technical test score.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param document: The document dictionary containing the Application ID needed to be updated.
    :param score: The technical test score that will be stored in the database.
    '''
    connection.Application.update( {'_id':document["_id"]}, {"$set": {"Test Results.Technical": score}}, upsert=True )

def check_cv_made(connection, candidate_id):
    '''
    Takes a document and a score, then using the document's ID it sets the Application's Technical test score.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidate_id: The ID of the candidate in question.
    :return: A boolean value displaying if the candidate has a CV stored in the database.
    '''
    candidate = connection.Candidate.find_one( {"_id": ObjectId(candidate_id)} )
    if "CVData" in candidate.keys():
        return True
    return False

def insert_cv(connection, candidate_id, cv_data):
    '''
    Takes a candidate ID and a dictionary containing that candidate's inputted CV data and then updates the database to store it.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidate_id: The ID of the candidate in question.
    :param CVData: The dictionary containing the CV data to be stored int he database.
    '''
    connection.Candidate.update_one( {"_id": ObjectId(candidate_id)}, {"$set": {"CVData": cv_data}}, upsert=False)

def is_job_already_created(connection, job_name):
    '''
    Checks if the entered name is stored as the name of any job currently when all spaces are stripped.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_name: The name of the job to be checked.
    :return: A boolean value determining if the job is already created in the system.
    '''
    job_names = connection.Job.distinct("Job Name")
    if job_name in job_names:
        return True
    if job_name.replace(" ", "") in job_names:
        return True
    for stored_name in job_names:
        if job_name == stored_name.replace(" ", ""):
            return True
    return False

def create_job(connection, document):
    '''
    Inserts a new job docuemnt into the database.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param document: The dictionary containing the new job document to be added to the database.
    '''
    connection.Job.insert_one(document)

def get_community_contributions(connection, candidate_id):
    '''
    Returns a score regarding the contributions a specific candidate has made on Github

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidate_id: The ID of the candidate in question.
    :return: An integer value determining the score a candidate achieved in the community contributions test.
    '''
    candidate = dict(connection.Candidate.find_one( {"_id": candidate_id} ))
    if "CVData" in candidate.keys():
        if "Github Username" in candidate["CVData"].keys():
            try:
                return get_public_contributions(candidate["CVData"]["Github Username"], "ec82888f3555dfb1fa9f7cf9092755cd0834b1e4")
            except:
                return 40
    else:
        return 0

def get_job(connection, job_id):
    '''
    Gets from the database the job document with the specified ID.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_id: The ID of the job in question.
    :return: Returns an integer value determining the score a candidate achieved in the community contributions test.
    '''
    job = connection.Job.find_one( {"_id":ObjectId(job_id)} )
    if job["Availability"]["End Date"] <= datetime.utcnow():
        job["Closed"] = True
    return job

def create_job_shortlist(connection, job_id):
    '''
    Takes a job ID and iterates through the applications that have been made to that job and using the Machine Learning model followed by a ranking of the candidate's scores stores the amount of candidates required by the job in the database.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_id: The ID of the job in question.
    '''
    job = get_job(connection, job_id)
    candidate_IDs = list(connection.Application.find( {"Job ID": ObjectId(job_id)},{"Candidate ID":1, "_id":0} ))

    candidate_list = []
    for candidate in candidate_IDs:
        candidate_list.append(connection.Candidate.find_one( {"_id":ObjectId(candidate["Candidate ID"])} ))

    shortlist = get_best_candidates(connection, job, evaluate_candidates(connection, candidate_list, job["Job Name"].replace(" ", "")))

    connection.Job.update( {"_id":ObjectId(job_id)}, {"$set": {"Latest Shortlist":shortlist}}, upsert=True)

def evaluate_candidates(connection, candidates, job_name):
    '''
    Takes a list of candidates and the name of the job being applied for and returns a dictionary of the candidates grouped innto a classification from 1 to 10.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidates: A list of candidates to be evaluated by the machine learning model.
    :param job_name: The name of the job being evaluated, used to determine the name of the machine learning model to use.
    :return: A dictionary containing all the candidates classified into groups from 1 to 10.
    '''
    ml_object = ml.MLModel(job_name, "machinelearning/models/")
    ranked_candidates = dict([(1, []), (2, []), (3, []), (4, []), (5, []), (6, []), (7, []), (8, []), (9, []), (10, [])])
    for candidate in candidates:
        cv = ml_object.extract_json(candidate, ml_object.exemplarCV)
        rank = ml_object.predict(cv)
        ranked_candidates[classify(rank)].append(candidate["_id"])

    return ranked_candidates

def classify(x):
    '''
    Takes a value for the rank assigned to a candidate by the machine learning model and classifies it into a grouping from 1 to 10.

    :param rank: A rank returned by the machine learning model evaluation.
    :return: An integer value from 1 to 10 depicting the classification the rank should fit into.
    '''
    if (x[0] >= 0 and x[0] < 0.1):
        return 1
    elif (x[0] >= 0.1 and x[0] < 0.2):
        return 2
    elif (x[0] >= 0.2 and x[0] < 0.3):
        return 3
    elif (x[0] >= 0.3 and x[0] < 0.4):
        return 4
    elif (x[0] >= 0.4 and x[0] < 0.5):
        return 5
    elif (x[0] >= 0.5 and x[0] < 0.6):
        return 6
    elif (x[0] >= 0.6 and x[0] < 0.7):
        return 7
    elif (x[0] >= 0.7 and x[0] < 0.8):
        return 8
    elif (x[0] >= 0.8 and x[0] < 0.9):
        return 9
    else:
        return 10
    '''
    for x in range(1, 11):
        if rank[0] < x/10:
            return x
    return 10
    '''
    
def get_best_candidates(connection, job, classified_data):
    '''
    Takes the dictionary of classified candidates and returns the top ranking candidates based on the average of their test scores.
    This works by iterating the keys in the classified_data dictionary in reversed order (From 10 to 1) each time extracting the candidates if it would stay below the quota of applicants to recieve. When the threshold would be reached the candidates are ranked by their average test score and removed from best to worst.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job: A list of candidates to be evaluated by the machine learning model.
    :param classified_data: A dictionary containing all the applicants calssified into categories from 1 to 10.
    :return: A list of the final shortlist of candidates chosen.
    '''
    for key in classified_data.keys():
        print(key, len(classified_data[key]))

    applicants_found = 0
    applicant_number = int(job["Applicants Required"])
    final_applicants = []
    classification_keys = classified_data.keys()
    classification_keys.reverse()
    for key in classification_keys:
        applicants_found += len(classified_data[key])
        if applicants_found > applicant_number:
            ranking = []
            for candidate_id in classified_data[key]:
                ranking.append((candidate_id, get_test_score(connection, candidate_id, job["_id"])))
            ranking.sort(key=lambda tup: tup[1])

            while len(final_applicants) < applicant_number:
                top_candidate = ranking.pop()
                final_applicants.append(top_candidate[0])
                applicants_found += 1
            break
        else:
            final_applicants.extend(classified_data[key])
    return final_applicants

def get_test_score(connection, candidate_id, job_id):
    '''
    Takes a candidate ID and a job ID and finds the corresponding appplication before returning the average of their test scores therein.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param candidate_id: The ID of the candidate in question.
    :param job_id: The ID of the job in question.
    :return: The mean of a candidates test scores.
    '''
    application = connection.Application.find_one( {"Candidate ID": ObjectId(candidate_id), "Job ID":ObjectId(job_id)} )
    
    return mean(application["Test Results"].values())

def get_applied_number(connection, job_id):
    '''
    Returns the amount of applications made to a specific job.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_id: The ID of the job in question.
    :return: An integer value  of how many applicaitons were made to the job in question.
    '''
    return int(connection.Application.count( {"Job ID": ObjectId(job_id)} ))

def set_job_completed(connection, job_id):
    '''
    Sets the Closed field in the document for a specific job in the Job collection to tell the system the job has been completed and feedback has been made.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_id: The ID of the job in question.
    '''
    connection.Job.update( {"_id":ObjectId(job_id)}, {"$set": {"Completed":True}}, upsert=True)

def get_job_names(connection):
    '''
    Returns a list of all the names of the jobs in the system.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :return: A list of job names stored in the system.
    '''
    return connection.Job.distinct("Job Name")

def get_job_by_name(connection, job_name):
    '''
    Returns the document for a specific job by it's name.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param job_name: The name of the job to be returned.
    :return: The dictionary containing the entire document for the specified job.
    '''
    return connection.Job.find_one( {"Job Name": job_name} )

def reinforce_model(connection, model_name, label, candidate_ids):
    '''
    Takes the name of a machine learning model and reinforces it with a list of CVs and labels for them.

    :param connection: A connection to the mongo database to allow queries to be made thereon.
    :param model_name: The name of the model to be reinforced.
    :param label: A list of all the labels attributed to candidates.
    :param candidate_ids: A list of candidate IDs who have been returned fro feedback to the machine learning model.
    '''
    candidates = []
    for candidate_id in candidate_ids:
        candidates.append(get_candidate(connection, candidate_id))
    ml_object = rm.ReinforcedModel(model_name, "machinelearning/models/")
    ml_object.reinforce(label, candidates)
