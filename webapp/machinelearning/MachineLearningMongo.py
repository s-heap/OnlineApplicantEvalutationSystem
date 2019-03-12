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

import data as d
import functions as f
from mlmodeltrainer import MLModelTrainer
from mlmodel import MLModel
from reinforcedmodel import ReinforcedModel
import math
import json 
import pickle


import click
from flask import Flask
from flask import current_app, g
from flask.cli import with_appcontext
from flask_pymongo import PyMongo



def create_model(dataset, exemplarCV, modelName):
    print("************************NEW RUN************************")
    mlObj = MLModelTrainer(dataset)
    mlObj.setExemplarCV(exemplarCV)
    print("*******************DICTIONARY CREATED******************")
    print("***********************DATA LOADED*********************")

    _X_train, Y_train, _X_test, Y_test = mlObj.split_data(0, 99900)
    print("***********************DATA SPLIT**********************")
    X_train = mlObj.scale_data(_X_train)
    X_test = mlObj.scale_data(_X_test)
    # print(X_test[0])
    print("***********************DATA SCALED*********************")

    mlObj.fit(X_train, Y_train)
    print("***********************DATA TRAINED********************")
    mlObj.test(X_test, Y_test)
    print("***********************DATA TESTED*********************")
    data=mlObj.getDataset()

    mlObj.saveModel(modelName)
    mlObj.saveModelData(modelName, _X_train, _X_test, Y_train, Y_test)

create_model('cvDataset.json', 'cvExample.json', 'javaModel2')


javaModel = MLModel("javaModel2")
count={"good":0,"reject":0,"ideal":0,"poor":0}
count3={"1":0,"2":0,"3":0,"4":0, "5":0, "6":0, "7":0, "8":0, "9":0, "10":0}

for i in range(99900, 99950):
    cv = javaModel.extract_json(javaModel.getDataset(), i, javaModel.exemplarCV)
    x=javaModel.predict(cv)
    
    if (x[0] >= 0 and x[0] < 0.1):
         count3["1"]=count3["1"]+1
    elif (x[0] >= 0.1 and x[0] < 0.2):
        count3["2"]=count3["2"]+1
    elif (x[0] >= 0.2 and x[0] < 0.3):
        count3["3"]=count3["3"]+1
    elif (x[0] >= 0.3 and x[0] < 0.4):
        count3["4"]=count3["4"]+1
    elif (x[0] >= 0.4 and x[0] < 0.5):
        count3["5"]=count3["5"]+1
    elif (x[0] >= 0.5 and x[0] < 0.6):
        count3["7"]=count3["7"]+1
    elif (x[0] >= 0.6 and x[0] < 0.7):
        count3["8"]=count3["8"]+1
    elif (x[0] >= 0.7 and x[0] < 0.8):
        count3["9"]=count3["9"]+1
    elif (x[0] >= 0.8 and x[0] < 0.9):
        count3["10"]=count3["10"]+1
 
print(count3)
javaRLModel = ReinforcedModel("JavaModel2")
for i in range(99950, 100000):
    cv = javaModel.extract_json(javaModel.getDataset(), i, javaModel.exemplarCV)
    javaRLModel.reinforce("10", cv)
javaRLModel.setXtrain(javaRLModel.scale_data(javaRLModel.getXtrain()))
javaRLModel.setXtest(javaRLModel.scale_data(javaRLModel.getXtest()))
javaRLModel.fit()
javaRLModel.test()