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

import math
import json
import pickle

from mlutility import MLUtility



class MLModel(MLUtility):
    '''
    The MLModel object contains the stored data associated with the model name
    and allows for predictions to be made on supplied cvs.
    
    :param modelName: The name of the model to use
    :type modelName: str
    :param directory: The name of the directory where the model is stored
    :type directory: str
    :ivar directory: This is where directory is stored
    :type directory: str
    :ivar mlp: This is where the ml model is stored
    :type mlp: str
    :ivar word_to_id: This is where the word list is stored
    :type word_to_id: dictionary(str, int)
    :ivar m: This is where the length of the word list is stored
    :type m: int
    :ivar exemplarCV: This is where the exemplar cv is stored in json format
    :type exemplarCV: json[]
    :ivar exemplarCV: This is where the exemplar cv is stored as a vector 
    :type exemplarCV_vector: float[]
    :ivar exemplarCV: This is where the dataset is stored in json format
    :type cvDataset: json[]
    '''
    def __init__(self, modelName, directory):
        self.directory = directory+modelName+"/"
        self.mlp = pickle.load(open(self.directory+modelName+".sav", 'rb'))
        self.word_to_id = pickle.load(open(self.directory+modelName+"_word_list.sav", 'rb'))
        # self.m = pickle.load(open(directory+modelName+"_word_list_len.sav", "rb"))
        self.m = len(self.word_to_id)

        self.exemplarCV = pickle.load(open(self.directory+modelName+"_exemplar_cv.sav", "rb"))

        self.exemplarCV_vector = pickle.load(open(self.directory+modelName+"_exemplar_cv_vector.sav", "rb"))
        #self.cvDataset = pickle.load(open(self.directory+modelName+"_dataset.sav", "rb"))
        

    def getDataset(self):
        """Return the cv dataset stored by the model"""
        return self.cvDataset
    def getExemplarCV_vector(self):
        """Return the exemplar cv stored by the model"""
        return self.exemplarCV_vector
    def predict(self, cv):
        """Get a ranking for a candidates cv
        
        Keyword arguments:
        cv -- candidates cv
        """
        try:
            prepared_vector=[]
            test_vector = [0.0]*self.m
            test_vector = self.generate_vector(cv)
            prepared_vector.append(test_vector)
            prepared_vector=self.scale_data(prepared_vector)
            
            result=self.mlp.predict(prepared_vector)
            return (self._cosine_similarity(test_vector, self.getExemplarCV_vector()),result)
        except:
            return False
