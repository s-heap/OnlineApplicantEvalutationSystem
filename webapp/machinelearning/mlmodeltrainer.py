"""
Author: u1711644
Date last modified: 27/02/19
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
import webapp.db as db

from mlutility import MLUtility

import math
import json
import pickle




class MLModelTrainer(MLUtility):
    '''
    The MLModelTrainer object contains the stored data associated with the
    model name and allows for predictions to be made on supplied cvs.
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
    :ivar n: amount of cvs to get from database
    :type n: int
    '''
    word_to_id = {}

    def __init__(self, n):
        self.cvDataset = self.get_cvs(n)
        print("\n\n\n")
        print(len(self.cvDataset))
        print("\n\n\n")

        x = self.create_word_list()
        self.word_to_id = x[0]
        self.m = x[1]
        self.mlp = MLPClassifier(hidden_layer_sizes=(13,13,13),max_iter=500)

    def setExemplarCV(self, exemplarCV):
        '''Sets the exemplar cv and create its vector as well
        
        :param exemplarCV: takes in the exemplar cv after the object has
                           been instanstiated
        '''
        self.exemplarCV = exemplarCV
        self.exemplar_data = self.flatten_ideal_cv()
        self.exemplar_vector = self.generate_vector(self.exemplar_data)

    def getDataset(self):
        '''Gets the cv dataset stored by the model'''
        return self.cvDataset

    def getExemplarCV(self):
        '''Gets the exemplar cv stored by the model'''
        return self.exemplarCV

    def getExemplarCV_vector(self):
        '''Gets the exemplar cvs vector stored by the model'''
        return self.exemplar_vector

    def tweak_nn_params(self):
        '''todo: allows parameters of nn to be tweaked (advanced user mode) '''
        pass

    def candidate_classifier(self, cosine_rank):
        '''Places cv into a cluster based on its cosine rank. The clusters are
        all integers between 1 and 10 inclusive

        :param cosine_rank: passes in a number representing how similar the 
                            candidate cv was to the model cv
        :return: cluster cv was placed into 
        '''
        if (cosine_rank >= 0 and cosine_rank < 0.1):
            return "1"
        elif (cosine_rank >= 0.1 and cosine_rank < 0.2):
            return "2"
        elif (cosine_rank >= 0.2 and cosine_rank < 0.3):
            return "3"
        elif (cosine_rank >= 0.3 and cosine_rank < 0.4):
            return "4"
        elif (cosine_rank >= 0.4 and cosine_rank < 0.5):
            return "5"
        elif (cosine_rank >= 0.5 and cosine_rank < 0.6):
            return "6"
        elif (cosine_rank >= 0.6 and cosine_rank < 0.7):
            return "7"
        elif (cosine_rank >= 0.7 and cosine_rank < 0.8):
            return "8"
        elif (cosine_rank >= 0.8 and cosine_rank < 0.9):
            return "9"
        elif (cosine_rank >= 0.9 and cosine_rank < 1):
            return "10"

    def create_word_list(self):
        '''Create a dictionary of all unique words as the key
        with its numerical representation as the value. The 
        numerical representation is the length of the 
        dictionary at the time the key was added

        :return: Returns a tuple of the word_list and its length
        '''
        word_list={}
        # Generalise all universties as good or bad as a list of approved ones
        # are supplied
        word_list['GoodUni'] = len(word_list)
        word_list['BadUni'] = len(word_list)
        # Degree is generalised as well
        word_list['GoodDegree'] = len(word_list)
        word_list['BadDegree'] = len(word_list)

        for feature in self.get_feature_collection():
            for word in feature:
                if word not in word_list:
                    word_list[word] = len(word_list)
        # 0 count given for non existent words
        m = len(word_list)
        return (word_list, m)

    def get_feature_collection(self):
        connection = db.get_connection()
        drop_downs= db.get_drop_down_lists(connection)
        print(drop_downs["Degree Level"])
        return [drop_downs["Languages Known"], drop_downs["Skills"], drop_downs["Degree Level"], drop_downs["Previous Employment Position"]]
        
    def flatten_ideal_cv(self):
        '''Converts the JSON data into a 1D array so it can be turned into a vector

        :return: 1D array containing all features in the ideal cv
        '''
        arr=[]
        # ideal cv will contain a good degree
        arr.append('GoodDegree') 
        # gives a 1 in the correct degree level
        arr.append(self.exemplarCV['Degree Level']) 
        # ideal cv will contain a good uni
        arr.append('GoodUni') 
        # adds all required languages. To increase weighting added n times 
        # where n is the expertise level
        for i in range(len(self.exemplarCV['Languages Known'])):
            for j in range(int(self.exemplarCV['Languages Known'][i]['Expertise'])):
                arr.append(self.exemplarCV['Languages Known'][i]['Language'])
        
        # adds all required skills. To increase weighting added n times 
        # where n is the expertise level
        for i in range(len(self.exemplarCV['Skills'])):
            for j in range(int(self.exemplarCV['Skills'][i]['Expertise'])):
                arr.append(self.exemplarCV['Skills'][i]['Skill'])
        
        # adds all required languages. To increase weighting added n times 
        # where n is the time worked in the role in months
        for i in range(len(self.exemplarCV['Previous Employment'])):
            length = self._months_worked(self.exemplarCV['Previous Employment'][i]['Length of Employment'])
            for j in range(length):
                arr.append(self.exemplarCV['Previous Employment'][i]['Position'])
        return arr

    def split_data(self, start, end):
        '''Split the data into the training set and test set. Also calls
        the function to convert the data into a vector.

        :param start: where in the cv dataset to start getting cvs from
        :type start: where in the cv dataset to stop getting cvs from

        :return: a tuple containing the training data, training labels, testing
                 data, and testing labels
        '''
        #initialise variables
        split = int((end*0.8))
        X=[]
        y=[]
        X_tests = []
        y_tests = []

        for i in range (start, end):
            # covert cv into 1D array
            current_cv = self.extract_json(self.cvDataset[i], self.exemplarCV) 
            # initalise vector
            current_vector = [0.0]*self.m
            # call generate vector function from mlutility and store in c_v
            current_vector = self.generate_vector(current_cv)
            # find how similar the candidate is to the model cv
            cosine_similarity = self._cosine_similarity(current_vector, self.exemplar_vector)
            if i < split: # training set
                X.append(current_vector)
                y.append(self.candidate_classifier(cosine_similarity))
            else:         # testing set
                X_tests.append(current_vector)
                y_tests.append(self.candidate_classifier(cosine_similarity))

        return (X, y, X_tests, y_tests)



    def fit(self, X_train, y_train):
        '''run the ml model 

        :param X_train: take in the training data
        :type X_train: float[]
        :param y_train: take in the training labels
        :type y_train: float[]
        '''
        self.mlp.fit(X_train, y_train)

    def test(self, X_test, y_test):
        '''test the ml model and output results to console

        :param X_test: take in the test data
        :type X_test: float[]
        :param y_test: take in the test labels
        :type y_test: float[]
        '''
        predictions = self.mlp.predict(X_test)
        print(confusion_matrix(y_test,predictions))
        print(classification_report(y_test,predictions))

    def saveModel(self, filename, directory):
        '''save the model using pickle to serialize it. It stores in the 
        supplied directory as the given filename. Directory should 
        currently be machinelearning/models, this will change if system is
        deployed so is not hard coded.

        :param filename: Should be the job name so the model can be easily 
                         referenced later on
        :type filename: str
        :param directory: Directory to save the model in
        :type directory: str
        '''
        # set the filenames for all data to be saved
        ml = filename+'.sav'
        word_list = filename+'_word_list.sav'
        word_list_len = filename+'_word_list_len.sav'
        exemplar_cv = filename+"_exemplar_cv.sav"
        exemplar_cv_vector = filename+"_exemplar_cv_vector.sav"
        list_of_cvs = filename+"_dataset.sav"
        
        # create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        pickle.dump(self.mlp, open(directory+ml, 'wb'))
        pickle.dump(self.word_to_id, open(directory+word_list, 'wb'))
        pickle.dump(self.m, open(directory+word_list_len, 'wb'))
        pickle.dump(self.getExemplarCV_vector(), open(directory+exemplar_cv_vector, 'wb'))
        pickle.dump(self.getExemplarCV(), open(directory+exemplar_cv, 'wb'))
        pickle.dump(self.getDataset(), open(directory+list_of_cvs, 'wb'))


    def saveModelData(self, filename, directory, X_train, X_test, y_train, y_test):
        '''saves the training and test data for reinforced learning. Should be done
        after initial model save.

        :param filename: Should be the job name so the model can be easily 
                        referenced later on
        :type filename: str
        :param directory: Directory to save the model in
        :type directory: str
        :param X_train: take in the training data
        :type X_train: float[]
        :param y_train: take in the training labels
        :type y_train: float[]
        :param X_test: take in the test data
        :type X_test: float[]
        :param y_test: take in the test labels
        :type y_test: float[]
        '''
        x_train_d = filename+"_x_train.sav"
        x_test_d = filename+"_x_test.sav"
        y_train_d = filename+"_y_train.sav"
        y_test_d = filename+"_y_test.sav"
        # directory = filename+"/"
        if not os.path.exists(directory):
            os.makedirs(directory)

        pickle.dump(X_train, open(directory+x_train_d, 'wb'))
        pickle.dump(X_test, open(directory+x_test_d, 'wb'))
        pickle.dump(y_train, open(directory+y_train_d, 'wb'))
        pickle.dump(y_test, open(directory+y_test_d, 'wb'))
