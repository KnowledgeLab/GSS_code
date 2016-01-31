# -*- coding: utf-8 -*-
"""
Created on Fri Nov 08 16:56:16 2013

@author: Misha
"""


import cPickle as cp
from random import sample
import sys

sys.path.append('../Code/')
from articleClass import *
pathToData = '../Data/'
articleClasses = cp.load(open(pathToData + 'articleClasses.pickle', 'rb'))

print sample([int(el.articleID) for el in articleClasses], 20)