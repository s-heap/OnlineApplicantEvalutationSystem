"""
Author: u1711644
Date last modified: 27/02/19
"""
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

# import data as d
# import functions as f
from mlutility import MLUtility

import math
import json
import pickle


import click
from flask import Flask
from flask import current_app, g
from flask.cli import with_appcontext
from flask_pymongo import PyMongo

class ReinforcedModel(MLUtility):
    '''
    The ReinforcedModel class contains the stored data associated with the
    model name and allows for the model to be updated via feedback from the
    client so the model is more accurate the next time a position opens for
    that job
    :param modelName: The name of the model to use
    :type modelName: str
    :param directory: The name of the directory where the model is stored
    :type directory: str
    :ivar directory: This is where the directory is stored
    :type directory: str
    :ivar exemplarCV: This is where word list is stored
    :type mlp: str
    :ivar word_to_id: This is where the list of unique words is stored
    :type word_to_id: dictionary(str, int)
    :ivar m: Stores length of list of unique words is stored
    :type m: int
    :ivar exemplarCV: Stores the exemplar cv retrieved from the database
    :type exemplarCV: json[]
    :ivar exemplarCV_vetor: Stores the vector of the exemplar cv
    :type exemplarCV_vector: float[]
    :ivar cvDataset: stores the cv dataset retrieved from the database
    :type cvDataset: json[]
    '''
    def __init__(self, modelName, directory):
        self.directory = directory+modelName+"/"
        self.filename = modelName
        # print("\n\n")
        # print(modelName)
        # print(directory)
        # print(self.directory)
        # print(self.directory+modelName)
        # print("\n\n")

        self.mlp = pickle.load(open(self.directory+modelName+".sav", 'rb'))
        self.word_to_id = pickle.load(open(self.directory+modelName+"_word_list.sav", 'rb'))
        self.m = len(self.word_to_id)
        self.exemplarCV = pickle.load(open(self.directory+modelName+"_exemplar_cv.sav", "rb"))
        self.exemplarCV_vector = pickle.load(open(self.directory+modelName+"_exemplar_cv_vector.sav", "rb"))
        self.cvDataset = pickle.load(open(self.directory+modelName+"_dataset.sav", "rb"))

        self.X_train = pickle.load(open(self.directory+modelName+"_x_train.sav", 'rb'))
        self.X_test = pickle.load(open(self.directory+modelName+"_x_test.sav", 'rb'))
        self.Y_train = pickle.load(open(self.directory+modelName+"_y_train.sav", 'rb'))
        self.Y_test = pickle.load(open(self.directory+modelName+"_y_test.sav", 'rb'))

    def reinforce_single(self, label, candidate):
        '''Update dataset with a single candidates cv label

        :param label: 1-10 ranking of label
        :type label: int
        :param candidate: candidates cv
        :type candidate: json
        '''
        l = label
        # if label is too large or small give max/min val
        if l > 10:
            l = 10
        elif l < 1:
            l = 1
        # create 1D array            
        cv = self.extract_json(candidate, self.exemplarCV)
        prepared_vector=[]
        # generate vector
        test_vector = [0.0]*self.m
        test_vector = self.generate_vector(cv)
        prepared_vector.append(test_vector)
        prepared_vector=self.scale_data(prepared_vector)
        # add to dataset
        self.X_train.append(prepared_vector[0])
        self.Y_train.append(l)
        
    def reinforce(self, labels, candidates):
        '''Method which calls reinforce_single to reinforce a list
        of candidates at once

        :param labels: list of labels
        :type labels: int[]
        :param candidates: list of candidate cvs
        :type candidates: json
        '''
        for i in range(len(candidates)):
            self.reinforce_single(labels[i], candidates[i])
        x_train_d = self.filename+"_x_train.sav"
        y_train_d = self.filename+"_y_train.sav"
        # saves dataset after reinforcing 
        pickle.dump(self.X_train, open(self.directory+x_train_d, 'wb'))
        pickle.dump(self.Y_train, open(self.directory+y_train_d, 'wb'))

    def fit(self):
        '''Train the reinforced model'''
        self.mlp.fit(self.X_train, self.Y_train)

    def test(self):
        '''Test the reinforced model'''
        predictions = self.mlp.predict(self.X_test)
        print(confusion_matrix(self.Y_test, predictions))
        print(classification_report(self.Y_test, predictions))

    def getXtrain(self):
        '''Return candidate cv training list'''
        return self.X_train

    def getXtest(self):
        '''Return candidate cv testing list'''
        return self.X_test

    def setXtrain(self, arr):
        '''Set candidate cv list
        
        :param arr: new X_train
        '''
        self.X_train = arr

    def setXtest(self, arr):
        '''Set candidate cv list
        
        :param arr: new X_test
        '''
        self.X_test = arr

    def saveModelData(self):
        '''Saves the training and test data to store reinforced model'''
        x_train_d = self.filename+"_x_train.sav"
        x_test_d = self.filename+"_x_test.sav"
        y_train_d = self.filename+"_y_train.sav"
        y_test_d = self.filename+"_y_test.sav"
        ml = self.filename+'.sav'
        # directory = filename+"/"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        pickle.dump(self.X_train, open(self.directory+x_train_d, 'wb'))
        pickle.dump(self.X_test, open(self.directory+x_test_d, 'wb'))
        pickle.dump(self.Y_train, open(self.directory+y_train_d, 'wb'))
        pickle.dump(self.Y_test, open(self.directory+y_test_d, 'wb'))
        pickle.dump(self.mlp, open(self.directory+ml, 'wb'))
