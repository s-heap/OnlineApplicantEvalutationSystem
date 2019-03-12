import sys
import math
import sys 
import test_codingTest as x

s = x.Solution()

def test_1():
    return s.permute([1,2,3]) == 6

def test_2():
    return s.permute([1,2,3,4,5,6,7,8,9,0]) == 3628800

def test_3():
    return s.permute([0]) == 1

def test_4():
    try:
        s.permute(0)
        return False
    except:
        return True


def test_5():
    return s.permute([]) == 0

def run_tests():
    return [test_1(), test_2(), test_3(), test_4(), test_5()]

def run_tests_candidate():
    return [test_1(), test_2(), test_3()]
