# -*- coding: utf-8 -*-
"""
Created on Mon Sep 09 13:57:25 2013

@author: Misha
"""

class articleClass():
    # attributes
    articleID = None
    IVs = []
    DV = []
    controls = []
    centralIVs = []
    GSSYearsUsed = []
    GSSYearsPossible = []
    missingValues = [] #? 
    '''there's a missingValues dict in the data file missingValues = {"someNumvar1": {"values": [999, -1, -2]},  # discrete values
                 "someNumvar2": {"lower": -9, "upper": -1}, # range, cf. MISSING VALUES x (-9 THRU -1)
                 "someNumvar3": {"lower": -9, "upper": -1, "value": 999},
                 "someStrvar1": {"values": ["foo", "bar", "baz"]},
                 "someStrvar2": {"values': "bletch"}}
                 '''
    
    # methods
    def __init__(self, articleID=None, IVs=[], DVs=[], controls=[], centralIVs=[], GSSYearsUsed=[], GSSYearsPossible=[]):
        self.articleID = articleID
        self.IVs = IVs
        self.DVs = DVs
        self.controls = controls
        self.centralIVs = centralIVs
        self.GSSYearsUsed = GSSYearsUsed
        self.GSSYearsPossible = GSSYearsPossible
