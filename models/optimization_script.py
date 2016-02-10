# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 16:09:49 2013

@author: Dinakar Gade, Sarah M.Ryan
Created for Class IE633x - Stochastic Programming, Spring 2013

This script calls the pyomo model and solves the problem

"""

from coopr.pyomo import * #import coopr
#setup solver
from coopr.opt import SolverFactory
opt = SolverFactory('cplex')
#specify model
from ReferenceModel import model
#instantiate the model with data
instance = model.create('/Users/dgade/Desktop/spclass/scenariodata/AverageScenario.dat')
#apply solver and load results
results = opt.solve(instance)
instance.load(results)
#display results
for j in instance.Plants:
    print "PlantOpen["+ str(j) + "] = ", instance.PlantOpen[j].value,\
    "PlantCapacity["+ str(j) + "] = ", instance.PlantCapacity[j].value #Note the ".value"





