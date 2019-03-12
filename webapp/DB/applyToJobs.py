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

def createApplicationCollection():

    jobIDs = list(get_connection().Job.find({}, {"_id": 1}))
    output = []
    for jobIDObject in jobIDs:
        jobID = jobIDObject["_id"]
        candidateIDs = list(get_connection().Candidate.find({}, {"_id": 1}))
        for candidate in candidateIDs[:int(len(candidateIDs)/100)]:
            testResults = {'Literacy': random.randint(1, 101), 'Numeracy': random.randint(1, 101), 'Abstract Reasoning': random.randint(
                1, 101), 'Community Contribution': random.randint(1, 101), 'Technical': random.randint(1, 101)}
            output.append(
                {"Candidate ID": candidate["_id"], "Job ID": jobID, "Test Results": testResults})
    connection = get_connection().Application
    connection.delete_many({})
    connection.insert_many(output)

createApplicationCollection()
