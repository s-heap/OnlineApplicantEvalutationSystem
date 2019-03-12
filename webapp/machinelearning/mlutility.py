"""
Author: u1711644
Date last modified: 6/03/19
"""

import click
from flask import Flask
from flask import current_app, g
from flask.cli import with_appcontext
from flask_pymongo import PyMongo

from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os

import re
import math
import json
import pickle

class MLUtility:
    '''
    The MLUtility class is a superclass for MLModel, MLModelTrainer and 
    ReinforcedModel. It contains methods shared across all the classes.
    :var scaler: scaler object from sklearn.processing to normalize data
    :type scaler: StandardScaler()
    '''

    scaler = StandardScaler()

    def __getConnection(self):
        '''Establish a connection to the database. Used do to package 
        conflicts attempting to get connection from db.py

        :return: connection to the mongo database
        '''
        app = Flask(__name__)
        app.config['MONGO_URI'] = 'mongodb://localhost:27017/SeeVDB'
        mongo = PyMongo(app)
        return mongo.db

    def get_cvs(self, n):
        '''Return n cvs from the database
        
        :param n: amount of cvs to getch from db

        :return: list of candidates retrieved from the db
        '''
        return list(self.__getConnection().Candidate.find({},{"CVData":1, "_id":0}))[:n]

    def generate_vector(self, document):
        '''Turns the given document into a fixed sized vector which is the same
        length as the word list.

        :param document: candidates cv

        :return: returns the vectorized version of their cv
        '''
        vector = [0.0]*self.m
        for word in document:
            # gets numerical value of word
            word_id = self.word_to_id[word]
            # updates location where word is stored every time
            vector[word_id] += 1 
        return vector

    def _cosine_similarity(self, vector1, vector2):
        '''calculates how similar one vector is to another

        :param vector1: candidate cv
        :param vector2: model cv

        :return: returns the cosine similarity of the two vectors
        '''
        sums = 0.0
        norm1 = 0.0
        norm2 = 0.0
        for j in range(0, self.m):
            a = vector1[j]
            b = vector2[j]
            sums += a*b
            norm1 += a*a
            norm2 += b*b
        normalization = math.sqrt(norm1)*math.sqrt(norm2)
        cosine_similarity = sums/normalization
        return cosine_similarity
        
    def scale_data(self, arr):
        '''scale the data so it is normalized and ready for supervised learning
        
        :param arr: the arr to scale
        :type arr: float[][]

        :return: the scaled version of the array
        '''
        self.scaler.fit(arr)
        arr = self.scaler.transform(arr)
        return arr

    def _prepare_cv(self, vector):
        '''scale an indivdual vector

        :param arr: the arr to scale
        :type arr: float[]
        
        :return: scaled vector
        '''
        ret_vector = [vector]
        self.scaler.fit(ret_vector)
        ret_vector = self.scaler.transform(ret_vector)
        return  ret_vector

    def _months_worked(self, employment_length):
        '''Extracts the years and months worked from the standardised string
        given in the dataset and returns the total work time in months

        :param employment_length: how long they worked in said role
        :type employment_length: str

        :return: total time worked in months as an int
        '''
        arr = []
        list_of_nums = map(int, re.findall(r'\d+', employment_length))
        for i in list_of_nums:
            arr.append(i)
        if len(arr) == 2:
            return arr[0]*12 + arr[1]
        elif len(arr) == 1:
            return arr[0]
        else: # if they didnt work there at all and its just on their cv
            return 0

    def extract_json(self, candidate, exemplarCV):
        '''Extracts the json from the canidates cv and places it into a 
        1D array to allow for easy conversion to a vector. Compares 
        against the exemplarCV to check whether candidatte has an
        accepted uni/degree.

        :param candidate: candidate cv
        :type candidate: JSON
        :param exemplarCV: exemplar cv
        :type exemplarCV: JSON

        :return: 1D array version of candidate cv
        '''
        arr=[]
        languages_list=[]
        languages_expertise=[]
        skills_list=[]
        skills_expertise=[]
        months = 0
        years = 0

        # store languages known by example
        for i in range(len(exemplarCV['Languages Known'])):
            languages_list.append(exemplarCV['Languages Known'][i]['Language'])
            languages_expertise.append(exemplarCV['Languages Known'][i]['Expertise'])
        
        # store skills known by example
        for i in range(len(exemplarCV['Skills'])):
            skills_list.append(exemplarCV['Skills'][i]['Skill'])
            skills_expertise.append(exemplarCV['Skills'][i]['Expertise'])

        # check if candidates degree is in the approve degree list
        if (candidate['CVData']['Degree Qualification'] in exemplarCV["Approved Degree"]):
            arr.append('GoodDegree')
        else:
            arr.append('BadDegree')
        
        arr.append(candidate['CVData']['Degree Level'])
        
        # check if candidates uni is in the approve uni list
        if (candidate['CVData']['University Attended'] in exemplarCV["Approved Universities"]):
            arr.append('GoodUni')
        else:
            arr.append('BadUni')
        
        # add relevant languages candidate knows otherwise score will be lowered unecessarily
        for i in range(len(candidate['CVData']['Languages Known'])):
            # check if candidate knows language in the required list before adding it 
            if candidate['CVData']['Languages Known'][i]['Language'] in languages_list:
                index = languages_expertise[languages_list.index(candidate['CVData']['Languages Known'][i]['Language'])]
                iterations = min(int(candidate['CVData']['Languages Known'][i]['Expertise']), index)
                for j in range(iterations):
                    arr.append(candidate['CVData']['Languages Known'][i]['Language'])
        
        # add relevant skills candidate knows otherwise score will be lowered unecessarily
        for i in range(len(candidate['CVData']['Skills'])):
            # check if candidate knows skill in the required list before adding it 
            if candidate['CVData']['Skills'][i]['Skill'] in skills_list:
                index = languages_expertise[skills_list.index(candidate['CVData']['Skills'][i]['Skill'])]
                iterations = min(int(candidate['CVData']['Skills'][i]['Expertise']), index)
                for j in range(iterations):
                    arr.append(candidate['CVData']['Skills'][i]['Skill'])

        
        for i in range(len(candidate['CVData']['Previous Employment'])):
            length = self._months_worked(candidate['CVData']['Previous Employment'][i]['Length of Employment'])
            for j in range(length):
                arr.append(candidate['CVData']['Previous Employment'][i]['Position'])
        
        return arr
