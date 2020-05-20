'''
Created on 23.03.2011

@author: sergey
'''

class VerificationException(Exception):
    pass

class SeveralMathcingStatesException(VerificationException):
    pass

class ZeroMatchingStatesException(VerificationException):
    pass

class IncorrectStatesPathException(VerificationException):
    pass
