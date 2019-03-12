import sys
import math
import pytest
sys.path.insert(0, '../machinelearning')
import mlutility as mlu
import mlmodeltrainer as mlt
x = mlu.MLUtility()
# y = mlt.MLModelTrainer(10)
def test_get_cvs():
    assert len(x.get_cvs(10)) == 10

def test_generate_vector():
    x.generate_vector(["University of Warwick", "Java", "Java"])

def test_cosine_similarity_perp():
    assert x._cosine_similarity([0,1], [1,0]) == 0

def test_cosine_similarity_same():
    assert x._cosine_similarity([0,1], [0,1]) == 1

def test_months_worked_year():
    assert x._months_worked("1 years") == 1

def test_months_worked_month():
    assert x._months_worked("12 months") == 12

def test_months_worked_both():
    assert x._months_worked("4 years 5 months") == 53

def test_months_worked_none():
    assert x._months_worked("") == 0

def test_months_worked_erroneous():
    assert x._months_worked("fdsew") == 0



def test_creation():
    a = mlt.MLModelTrainer(10)

def test_setExemplarCV():
    pass

def test_getDataset():
    assert len(y.getDataset()) == 10

def test_getExemplarCV():
    pass

def test_getExemplarCV_vector():
    pass

def tweak_nn_params():
    pass

def test_candidate_classifier_extreme1():
    assert y.candidate_classifier(0) == "0"

def test_candidate_classifier_extreme2():
    assert y.candidate_classifier(1) == "10"

def test_candidate_classifier_erroneous1():
    assert y.candidate_classifier(-2) == "0"

def test_candidate_classifier_erroneous2():
    assert y.candidate_classifier(22) == "10"

def test_candidate_classifier_normal():
    assert y.candidate_classifier(0.43) == "3"

def test_create_word_list():
    assert len(y.create_word_list) == y.m