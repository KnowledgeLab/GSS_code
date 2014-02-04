"""
filename: put_variable_names_from_codebook_into_groups.py

Created on: Tue Jul 16 14:47:23 2013

author: Misha Teplitskiy

description: I have previously gone through the .txt version of the GSS Codebook and put dividers (the characters '***')
in between groups of variable names/descriptions that are conceptually related. This program takes that text file and 
creates a list of lists, where each inner list contains the names of the conceptually related variable.

input: the previously cleaned/partitioned .txt file containing GSS variable names and descriptions

output: groupsOfVariables.pickle, a (pickled) list-of-lists 

"""

