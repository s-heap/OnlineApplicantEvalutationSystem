import pymongo
import json
import pprint
import datetime
from flask import Flask
from flask_pymongo import PyMongo
import random
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from datetime import timedelta


def get_connection():
    app = Flask(__name__)
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/SeeVDB'
    mongo = PyMongo(app)
    return mongo.db


def createCandidateCollection():
    connection = get_connection().Candidate
    connection.delete_many({})
    connection.insert_many(loadCandidateDocuments())


def loadCandidateDocuments():
    with open('cvDataset.json', 'r') as f:
        CVDataset = json.load(f)
    output = []
    password_submit = generate_password_hash('password')
    for CV in CVDataset:
        document = {}
        document['Username'] = str(CV['Name']).replace(' ', '')
        document['Password'] = password_submit
        document['CVData'] = CV
        output.append(document)
    return output


def createJobCollection():
    connection = get_connection().Job
    connection.delete_many({})
    #connection.insert_many(loadJobDocuments(getEmployeeID()))


def getEmployeeID():
    employeeIDObject = get_connection().Employee.find_one({}, {"_id": 1})
    return employeeIDObject["_id"]


def loadJobDocuments(employeeID):
    jobDataSet = {}
    with open('testJobs.json', 'r') as f:
        jobDataSet = json.load(f)
    output = []
    current = datetime.utcnow()
    for job in jobDataSet:
        job['Employee ID'] = employeeID
        job["Availability"]["Date Created"] = current
        job["Availability"]["End Date"] = current + \
            timedelta(days=random.randint(5, 30))
        output.append(job)
    return output


def createInputFieldsCollection():
    connection = get_connection().InputFields
    connection.delete_many({})
    connection.insert_many(loadInputFieldsDocuments())


def loadInputFieldsDocuments():
    inputFieldsDataSet = {}
    with open('testInputFields.json', 'r') as f:
        inputFieldsDataSet = json.load(f)
    output = []
    for field in inputFieldsDataSet:
        output.append(field)
    return output


def createEmployeeCollection():
    connection = get_connection().Employee
    connection.delete_many({})
    employees = []
    password_submit = generate_password_hash('password')
    employees.append({'Username': 'employee1', 'Password': password_submit})
    employees.append({'Username': 'employee2', 'Password': password_submit})
    employees.append({'Username': 'employee3', 'Password': password_submit})
    connection.insert_many(employees)


def createApplicationCollection():
    connection = get_connection().Application
    connection.delete_many({})
    '''
    jobIDObject = get_connection().Job.find_one({}, {"_id": 1})
    jobID = jobIDObject["_id"]
    candidateIDs = list(get_connection().Candidate.find({}, {"_id": 1}))
    output = []
    for candidate in candidateIDs[:int(len(candidateIDs)/100)]:
        testResults = {'Literacy': random.randint(1, 101), 'Numeracy': random.randint(1, 101), 'Abstract Reasoning': random.randint(
            1, 101), 'Community Contribution': random.randint(1, 101), 'Technical': random.randint(1, 101)}
        output.append(
            {"Candidate ID": candidate["_id"], "Job ID": jobID, "Test Results": testResults})
    connection.insert_many(output)
    '''


def createTestQuestionsCollection():
    testQuestions = {}
    with open('testQuestions.json', 'r') as f:
        testQuestions = json.load(f)
    connection = get_connection().TestQuestions
    connection.delete_many({})
    connection.insert_many(list(testQuestions))


print("Creating Employee Collection")
createEmployeeCollection()
print("Creating Job Collection")
createJobCollection()
print("Creating InputFields Collection")
createInputFieldsCollection()
print("Creating Candidate Collection")
createCandidateCollection()
print("Creating Application Collection")
createApplicationCollection()
print("Creating TestQuestions Collection")
createTestQuestionsCollection()
