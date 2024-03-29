# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 14:48:28 2014

@author: Chan-Ching hsu
Created for Class IE633x - Stochastic Programming, Fall 2014

This model encodes the project problem
"""
import math, sys, random, copy, time
from random import randrange
#Make cplex package available
import cplex
from cplex.exceptions import CplexSolverError
#import solution_writer

  
def constraint2(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter):
#  global constCounter
  tempCoef = []
  tempList = []
  for i in range(scenario):
    for j in range(macro):
      tempList.append(compositionDelta[i][0][j][j])
      tempCoef.append(1)
      for k in range(small):
	if smallInBig[j].count(k) > 0:
	  tempList.append(compositionDelta[i][0][j][macro+k])
	  tempCoef.append(1)
      for k in range(ap):
	if apInBig[j].count(k) > 0:
	  tempList.append(compositionDelta[i][0][j][macro+small+k])
	  tempCoef.append(1)
      tempList.append(compositionBeta[0][j])
      tempCoef.append(-1)
      #print tempList
      #print tempCoef
    # if (len(tempList) != len(tempCoef)):
      #  print 'something wrong...'
      constCounter+=1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["available(2)_"+str(constCounter)+"#"+str(i)+'.'+str(0)+'.'+str(j)])
      del tempList[:]
      del tempCoef[:]
    for j in range(small):
      tempList.append(compositionDelta[i][1][j][macro+j])
      tempCoef.append(1)
      #for k in range(small):
      # if smallInBig[j].count(k) > 0:
	  #tempList.append(compositionTheta[i][0][j][macro+k])
	  #tempCoef.append(1)
      for k in range(ap):
	if apInSmall[j].count(k) > 0:
	  tempList.append(compositionDelta[i][1][j][macro+small+k])
	  tempCoef.append(1)
      tempList.append(compositionBeta[1][j])
      tempCoef.append(-1)
      #print tempList
      #print tempCoef
    # if (len(tempList) != len(tempCoef)):
      #  print 'something wrong...'
      constCounter+=1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["available(2)_"+str(constCounter)+"#"+str(i)+'.'+str(1)+'.'+str(j)])
      del tempList[:]
      del tempCoef[:]
    for j in range(ap):
      tempList.append(compositionDelta[i][2][j][macro+small+j])
      tempCoef.append(1)
      #for k in range(small):
      # if smallInBig[j].count(k) > 0:
	  #tempList.append(compositionTheta[i][0][j][macro+k])
	  #tempCoef.append(1)
      #for k in range(ap):
      # if apInSmall[j].count(k) > 0:
	  #tempList.append(compositionTheta[i][1][j][macro+small+k])
	  #tempCoef.append(1)
      tempList.append(compositionBeta[2][j])
      tempCoef.append(-1)
      #print tempList
      #print tempCoef
    # if (len(tempList) != len(tempCoef)):
      #  print 'something wrong...'
      constCounter+=1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["available(2)_"+str(constCounter)+"#"+str(i)+'.'+str(2)+'.'+str(j)])
      del tempList[:]
      del tempCoef[:]
  del tempList
  del tempCoef

  
def constraint1(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter):
  temp = 0
  consumPowDiff = []
  tempList = []
  for i in range(len(powerAct)):
    for j in range(len(powerAct[i])):
      consumPowDiff.append(powerAct[i][j] - powerSle[i][j])
      temp += powerSle[i][j]
  consumPowDiff.append(temp)
  for i in range(len(compositionAlpha)):
    tempList += compositionAlpha[i] 
  #tempList.append('dummyVar')
  #cpx.variables.add(names = ['dummyVar'])
  tempList.append('psilon')
#  addEnergy = [[] for i in range(3)]
#  addMacroEne = 6
#  addSmallEne = 3
#  addAPEne = 2
#  for i in range(len(addEnergy)):
#    if i == 0:
#      for j in range(macro):
#	addEnergy[i].append(addMacroEne)
#    elif i == 1:
#      for j in range(small):
#	addEnergy[i].append(addSmallEne)
#    else:
#      for j in range(ap):
#	addEnergy[i].append(addAPEne)

  for i in range(len(compositionDelta)):
    for j in range(len(compositionDelta[i])):
      for k in range(len(compositionDelta[i][j])):
	for l in range(len(compositionDelta[i][j][k])):
	  tempList.append(compositionDelta[i][j][k][l])
	  consumPowDiff.append(addEnergy[j][k]*prob[i])
  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = consumPowDiff)], senses = ["E"], rhs = [1], names = ["power_(1)_"+str(constCounter)])
#constCounter+=1
#cpx.linear_constraints.add(lin_expr = [[['dummyVar'], [1]]], senses = ["E"], rhs = [1], names = ["dummy_(0)_"+str(constCounter)])

  #temp = 0
  del tempList
  del consumPowDiff
	  
	  
def variable_creation(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario):
  varList = []
  for i in range(macro+small+ap):
    if i < macro:
      compositionLambda[0].append('lM'+str(i))
#      compositionMu[0].append('mM'+str(i))
    elif i < macro+small:
      compositionLambda[1].append('lS'+str(i-macro))
#      compositionMu[1].append('mS'+str(i-macro))
    else:
      compositionLambda[2].append('lA'+str(i-macro-small))
#      compositionMu[2].append('mA'+str(i-macro-small))
  for i in range(scenario):  
    compositionNu[i][0] = compositionNu[i][0] + [[] for j in range(macro)]
    compositionNu[i][1] = compositionNu[i][1] + [[] for j in range(small)]
    compositionNu[i][2] = compositionNu[i][2] + [[] for j in range(ap)]
    #for i in range(len(compositionNu[i]))
 
    for j in range(len(compositionNu[i])):
      if j == 0:
	for k in range(macro):
	  for l in range(location):
	    compositionNu[i][j][k].append('nM.'+str(i)+'.'+str(k)+'.'+str(l))
      elif j == 1:
	for k in range(small):
	  for l in range(location):
	    compositionNu[i][j][k].append('nS.'+str(i)+'.'+str(k)+'.'+str(l))
      elif j ==2:
	for k in range(ap):
	  for l in range(location):
	    compositionNu[i][j][k].append('nA.'+str(i)+'.'+str(k)+'.'+str(l))
  cpx.variables.add(names = [str(i) for i in (compositionLambda[0]+compositionLambda[1]+compositionLambda[2])], types = 'B' * (len(compositionLambda[0])+len(compositionLambda[1])+len(compositionLambda[2])))
#  cpx.variables.add(names = [str(i) for i in (compositionMu[0]+compositionMu[1]+compositionMu[2])], types = 'B' * (len(compositionMu[0])+len(compositionMu[1])+len(compositionMu[2])))
  for i in range(scenario):
    for k in range(len(compositionNu[i][0])):
      varList += compositionNu[i][0][k]
    for k in range(len(compositionNu[i][1])):
      varList += compositionNu[i][1][k]
    for k in range(len(compositionNu[i][2])):
      varList += compositionNu[i][2][k]
  cpx.variables.add(names = [str(i) for i in varList], types = 'B' * len(varList))
  del varList
  
  cpx.variables.add(names = [str(i) for i in (compositionAlpha[0]+compositionAlpha[1]+compositionAlpha[2]) ], types = "C" * (len(compositionAlpha[0])+len(compositionAlpha[1])+len(compositionAlpha[2])))
  cpx.variables.add(names = [str(i) for i in (compositionBeta[0]+compositionBeta[1]+compositionBeta[2]) ], types = "C" * (len(compositionBeta[0])+len(compositionBeta[1])+len(compositionBeta[2])))

  tempList = []
  for i in range(scenario):
  #for j in range(3):
    for k in range(macro):
      #for l in range(location):
	tempList += compositionTheta[i][0][k]
    for k in range(small):
      #for l in range(location):
      tempList += compositionTheta[i][1][k]
    for k in range(ap):
      #for l in range(location):
	tempList += compositionTheta[i][2][k]	
  cpx.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))	
  #ev.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
  del tempList[:]

  for i in range(scenario):
    #for j in range(3):
      for k in range(macro):
	#for l in range(location):
	  tempList += compositionDelta[i][0][k]
      for k in range(small):
	#for l in range(location):
	tempList += compositionDelta[i][1][k]
      for k in range(ap):
	#for l in range(location):
	  tempList += compositionDelta[i][2][k]
  cpx.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
  #ev.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))	
  del tempList

#  for i in range(scenario):
#   #for j in range(3):
#      for k in range(macro):
#	#for l in range(location):
#	tempList += compositionEta[i][0][k]
#      for k in range(small):
#	#for l in range(location):
#	tempList += compositionEta[i][1][k]
#      for k in range(ap):
#	#for l in range(location):
#	tempList += compositionEta[i][2][k]
#  cpx.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
#  #ev.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
#  del tempList
  
  cpx.variables.add(names = ['psilon'], types = "C")
  
  

def variable_matrix(scenario):
  compositionLambda = [[] for i in range(3)]
  #compositionMu = [[] for i in range(3)]
  compositionNu = [[[] for j in range(3)] for i in range(scenario)]
  compositionAlpha = [[] for i in range(3)]
  for i in range(macro):
    compositionAlpha[0].append('aM'+str(i))
  for i in range(small):
    compositionAlpha[1].append('aS'+str(i))
  for i in range(ap):
    compositionAlpha[2].append('aA'+str(i))
  #print compositionAlpha
  compositionBeta = [[] for i in range(3)]
  for i in range(macro):
    compositionBeta[0].append('bM'+str(i))
  for i in range(small):
    compositionBeta[1].append('bS'+str(i))
  for i in range(ap):
    compositionBeta[2].append('bA'+str(i))
    
  compositionTheta = [[[] for j in range(3)] for i in range(scenario)]
  for j in range(scenario):
    #for i in range(macro):
    #listToAdd = [1, 2, 3]
    compositionTheta[j][0] = compositionTheta[j][0] + [[] for i in range(macro)]
    compositionTheta[j][1] = compositionTheta[j][1] + [[] for i in range(small)]
    compositionTheta[j][2] = compositionTheta[j][2] + [[] for i in range(ap)]
    #for k in range(3):

    for l in range(macro):
      for i in range(location):
	compositionTheta[j][0][l].append('tM.'+str(j)+'.'+str(l)+'.'+str(i))
  #print compositionTheta[j][0][2]
      #compositionTheta[j][k].append([[] for i in range(small)])
    for l in range(small):
      for i in range(location):
	compositionTheta[j][1][l].append('tS.'+str(j)+'.'+str(l)+'.'+str(i))
      #compositionTheta[j][k].append([[] for i in range(ap)])
    for l in range(ap):
      for i in range(location):
	compositionTheta[j][2][l].append('tA.'+str(j)+'.'+str(l)+'.'+str(i))
	
  compositionDelta = [[[] for j in range(3)] for i in range(scenario)]
  for j in range(scenario):
    #for i in range(macro):
    #listToAdd = [1, 2, 3]
    compositionDelta[j][0] = compositionDelta[j][0] + [[] for i in range(macro)]
    compositionDelta[j][1] = compositionDelta[j][1] + [[] for i in range(small)]
    compositionDelta[j][2] = compositionDelta[j][2] + [[] for i in range(ap)]
    #for k in range(3):

    for l in range(macro):
      for i in range(location):
	compositionDelta[j][0][l].append('dM.'+str(j)+'.'+str(l)+'.'+str(i))
  #print compositionTheta[j][0][2]
      #compositionTheta[j][k].append([[] for i in range(small)])
    for l in range(small):
      for i in range(location):
	compositionDelta[j][1][l].append('dS.'+str(j)+'.'+str(l)+'.'+str(i))
      #compositionTheta[j][k].append([[] for i in range(ap)])
    for l in range(ap):
      for i in range(location):
	compositionDelta[j][2][l].append('dA.'+str(j)+'.'+str(l)+'.'+str(i))
	
#  compositionEta = [[[] for j in range(3)] for i in range(scenario)]
#  for j in range(scenario):
#    #for i in range(macro):
#    #listToAdd = [1, 2, 3]
#    compositionEta[j][0] = compositionEta[j][0] + [[] for i in range(macro)]
#    compositionEta[j][1] = compositionEta[j][1] + [[] for i in range(small)]
#    compositionEta[j][2] = compositionEta[j][2] + [[] for i in range(ap)]
#    #for k in range(3):
#
#    for l in range(macro):
#      for i in range(location):
#	compositionEta[j][0][l].append('uM.'+str(j)+'.'+str(l)+'.'+str(i))
#  #print compositionTheta[j][0][2]
#      #compositionTheta[j][k].append([[] for i in range(small)])
#    for l in range(small):
#      for i in range(location):
#	compositionEta[j][1][l].append('uS.'+str(j)+'.'+str(l)+'.'+str(i))
#      #compositionTheta[j][k].append([[] for i in range(ap)])
#    for l in range(ap):
#      for i in range(location):
#	compositionEta[j][2][l].append('uA.'+str(j)+'.'+str(l)+'.'+str(i))
  return compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta 
  
  
def preserved_scenario_model(scenario_number, preserved_scenario, preserved_scenario_prob, file_order):
  t1 = time.time()
  p = cplex.Cplex()
  p.parameters.mip.limits.treememory.set(8192)
  p.parameters.mip.strategy.file.set(3)
  p.objective.set_sense(p.objective.sense.maximize)
  p.parameters.threads.set(3)
  results_write_to = '../setupInfo/results_'+str(macro)+'_'+str(small)+'_'+str(ap)+'_'+str(max_user)+'_'+str(min_user)+'_o'+str(scenario_number)+'.log'
  #binaryVar(p)
  constCounter = 0
  compositionAlpha = []
  compositionBeta = []
  compositionDelta = []
  compositionLambda = []
  compositionNu = []
  compositionTheta = []
  compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta = variable_matrix(scenario_number)
  variable_creation(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number)
  constraint1(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter)
  constraint2(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter)
  delete(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter)
  constraint3(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario)
  constraint4(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario)
  constraint5(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario)
  
  priorToRemoval = p.linear_constraints.get_num()
  constraint6(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario)
#  remove_duplicate_constraints(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario)
#  correctifyConstNum(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario, priorToRemoval)
  
  constraint7(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario, priorToRemoval)
  constraint9(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario, priorToRemoval)
  constraint11(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario, priorToRemoval)
  constraint13(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario, priorToRemoval)
  #constraint14(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario, priorToRemoval)
  objective(p, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario_number, preserved_scenario_prob, constCounter, preserved_scenario, priorToRemoval)
  
  p.set_results_stream(results_write_to)
  p.set_log_stream(results_write_to)
  p.set_warning_stream(results_write_to)
  p.set_error_stream(results_write_to)
  
  t2 = time.time()
  print 'Constructing the '+str(file_order)+' model took '+str(t2 - t1)+' seconds.'
  filename_to_write = '../extensiveform/problem_'+str(macro)+'_'+str(small)+'_'+str(ap)+'_'+str(max_user)+'_'+str(min_user)+'_'+str(scenario_number)+'.lp'
  p.write(filename_to_write)
  print 'Finish writing the '+str(file_order)+' scenario-reduced problem for'+filename_to_write
  
  try:
    start_time = p.get_time()
    p.solve()
    end_time = p.get_time()
  except CplexSolverError, e:
    print "Exception raised during solve: "
    print e
  else:
    sol = p.solution
    
    print
    print "Solution status = ", sol.get_status(), ":",
    print sol.status[sol.get_status()]
    
    print "objective value: " + str(p.solution.get_objective_value())
    
    filename_to_write = '../extensiveform/obj.txt'
    fo = open(filename_to_write, 'a')
    fo.write(str(macro)+'_'+str(small)+'_'+str(ap)+'_'+str(max_user)+'_'+str(min_user)+'_'+str(scenario_number)+'\t'+str(t2-t1)+'\t'+str(p.solution.get_objective_value())+'\t'+str(end_time-start_time)+'\n')
    print 'Finish recording the objective value of the '+str(file_order)+' scenario-reduced problem...'
    fo.close()
    

def distance (xa, xb):
  return math.sqrt(math.pow(xa[0]-xb[0], 2) + math.pow(xa[1]-xb[1], 2))


def constraint14(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval):
  #global constCounter
#  for i in range(len(compositionDelta)):
#    for j in range(len(compositionDelta[i])):
#      for k in range(len(compositionDelta[i][j])):
#	for l in range(len(compositionDelta[i][j][k])):
#	  tempList.append(compositionDelta[i][j][k][l])
#	  tempCoef.append(utility[j][k])
#	  tempList.append('psilon')
#	  for m in range(location):
#	    if j == 0 and compositionDelta[i][j][k][l] == 'dM.'+str(i)+'.'+str(k)+'.'+str(m):
#	      tempCoef.append(-1*nUser[i][m]*0.5)
#	    elif j == 1 and compositionDelta[i][j][k][l] == 'dS.'+str(i)+'.'+str(k)+'.'+str(m):
#	      tempCoef.append(-1*nUser[i][m]*0.5)
#	    elif j == 2 and compositionDelta[i][j][k][l] == 'dA.'+str(i)+'.'+str(k)+'.'+str(m):
#	      tempCoef.append(-1*nUser[i][m]*0.5)
#	  constCounter += 1
#	  #tempCoef.append(-1*nUser[i][]*0.5)
#	  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [0], names = ["requirement_1(14)"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)])    
#	  del tempCoef[:]
#	  del tempList[:]
  tempList = []
  tempCoef = []
  for i in range(location):
    for j in range(len(compositionDelta)):
      for k in range(len(compositionDelta[j])):
	for l in range(len(compositionDelta[j][k])):
	
	  for m in range(len(compositionDelta[j][k][l])):
	    if k == 0 and compositionDelta[j][k][l][m] == 'dM.'+str(j)+'.'+str(l)+'.'+str(i):
	      tempList.append(compositionDelta[j][k][l][m])
	      tempList.append(compositionTheta[j][k][l][m])
	      tempCoef.append(utility[k][l])
	      tempCoef.append(-1*nUser[scenario_set[j]][i]*rand_BW[scenario_set[j]][i])
	    elif k ==1 and compositionDelta[j][k][l][m] == 'dS.'+str(j)+'.'+str(l)+'.'+str(i):
	      tempList.append(compositionDelta[j][k][l][m])
	      tempList.append(compositionTheta[j][k][l][m])
	      tempCoef.append(utility[k][l])
	      tempCoef.append(-1*nUser[scenario_set[j]][i]*rand_BW[scenario_set[j]][i])
	    elif k == 2 and compositionDelta[j][k][l][m] == 'dA.'+str(j)+'.'+str(l)+'.'+str(i):
	      tempList.append(compositionDelta[j][k][l][m])
	      tempList.append(compositionTheta[j][k][l][m])
	      tempCoef.append(utility[k][l])
	      tempCoef.append(-1*nUser[scenario_set[j]][i]*rand_BW[scenario_set[j]][i])
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [0], names = ["requirement_1(14)"+str(constCounter)+"#"+str(j)+'.'+str(l)+'.'+str(i)])    
      del tempCoef[:]
      del tempList[:]
  del tempCoef
  del tempList
  #return


def constraint13(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval):
  #global constCounter
  tempList = []
  tempCoef = []
  for i in range(len(compositionTheta)):
    for j in range(len(compositionTheta[i])):
      for k in range(len(compositionTheta[i][j])):
	tempList.append(compositionBeta[j][k])
	tempCoef.append(utility[j][k])
	for l in range(len(compositionTheta[i][j][k])):
	  tempList.append(compositionTheta[i][j][k][l])
	  for m in range(location):
	    if j == 0 and compositionTheta[i][j][k][l] == 'tM.'+str(i)+'.'+str(k)+'.'+str(m):
	      tempCoef.append(-1*nUser[scenario_set[i]][m]*rand_BW[scenario_set[i]][m])
	    elif j == 1 and compositionTheta[i][j][k][l] == 'tS.'+str(i)+'.'+str(k)+'.'+str(m):
	      tempCoef.append(-1*nUser[scenario_set[i]][m]*rand_BW[scenario_set[i]][m])
	    elif j == 2 and compositionTheta[i][j][k][l] == 'tA.'+str(i)+'.'+str(k)+'.'+str(m):
	      tempCoef.append(-1*nUser[scenario_set[i]][m]*rand_BW[scenario_set[i]][m])
	constCounter += 1
	cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [0], names = ["requirement_(13)"+str(constCounter)+"#"+str(j)+'.'+str(k)+'.'+str(m)])    
	del tempCoef[:]
	del tempList[:]
  del tempCoef
  del tempList
  return


def constraint12():
  global constCounter
  for i in range(0, len(compositionAlpha)-1):
    for j in range(len(compositionAlpha[i])):
      if i == 0:
	tempList.append(compositionAlpha[0][j])
	tempList.append(compositionBeta[0][j])
	constCounter += 1
	cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [0, -1])], senses = ["L"], rhs = [0], names = ["minimal_(12_0)"+str(constCounter)+"#"+str(j)])
	constCounter += 1
	cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [30, -1])], senses = ["G"], rhs = [0], names = ["maximal_(12_0)"+str(constCounter)+"#"+str(j)])
	del tempCoef[:]
	del tempList[:]
      elif i == 1:
	tempList.append(compositionAlpha[1][j])
	tempList.append(compositionBeta[1][j])
	constCounter += 1
	cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [0, -1])], senses = ["L"], rhs = [0], names = ["minimal_(12_1)"+str(constCounter)+"#"+str(j)])
	constCounter += 1
	cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [5, -1])], senses = ["G"], rhs = [0], names = ["maximal_(12_1)"+str(constCounter)+"#"+str(j)])
	del tempCoef[:]
	del tempList[:]
  return


def band_allocation():
#  global BigCor
#  global compositionBeta
#  global cpx, SmallCor, APCor, length, rbs, space, rap
  path = '../extensiveform/band_solution.txt'
  fo = open(path, "w")
  fo.write('\n\n#The following information is regarding bandwidth allocation to each station.\n')
  for i in range(len(compositionBeta)):
    for j in range(len(compositionBeta[i])):
      if i == 0:
	fo.write(str(cpx.solution.get_values(compositionBeta[i][j])/cpx.solution.get_values('psilon'))+" "+str(BigCor[j][0])+" "+str(BigCor[j][1])+" "+str(length+25)+" Macrocell_"+str(j)+"\n")
	if j == macro - 1:
	  fo.write('\n\n')
      elif i == 1:
	fo.write(str(cpx.solution.get_values(compositionBeta[i][j])/cpx.solution.get_values('psilon'))+" "+str(SmallCor[j][0])+" "+str(SmallCor[j][1])+" "+str(rbs/space)+" Macrocell_"+str(j)+"\n")
	if j == small - 1:
	  fo.write('\n\n')
      elif i == 2:
	fo.write(str(cpx.solution.get_values(compositionBeta[i][j])/cpx.solution.get_values('psilon'))+" "+str(APCor[j][0])+" "+str(APCor[j][1])+" "+str(rap/space)+" Macrocell_"+str(j)+"\n")
	if j == ap - 1:
	  fo.write('\n\n')
	  
  fo.write('#The following is the input to gnuplot to generate a figure of channel allocation.\n')
  fo.write('#plot \''+path+'\' index 0:0 using 2:3:1 notitle with labels, \''+path+'\' index 1:1 using 2:3:1 notitle with labels, \''+path+'\' index 2:2 using 2:3:1 notitle with labels, ')
  
  fo.write('\''+path+'\' index 0:0 using 2:3:4 title \'Macrocells\' with circles lc rgb \'#ccffcc\' fs transparent solid 0.4 border rgb \'black\', \''+path+'\' index 1:1 using 2:3:4 title \'Small cells\' with circles lc 2 lw 0.4, \''+path+'\' index 2:2 using 2:3:4 title \'Hot Spots\' with circles lc 5 lw 0.4\n')#, \''+path+'\' index 0:0 using 2:3 title \'Macrocell BSs\' with points lc 0, \''+path+'\' index 1:1 using 2:3 title \'Small cell BSs\' with points lc 8 ps 0.6, \''+path+'\' index 2:2 using 2:3 title \'APs\' with points lc 4 ps 0.6 pt 3\n')
   
  #f.write('\''+path+'\' index 0:0 using 2:3 title \'Macrocell BSs\' with points lc 0, \''+path+'\' index 1:1 using 2:3 title \'Small cell BSs\' with points lc 8 ps 0.6, \''+path+'\' index 2:2 using 2:3 title \'APs\' with points lc 4 ps 0.6 pt 3\n')
  
  
  fo.write('set size square\nset xrange[-50:2150]\nset yrange[-50:2150]\nset object 1 rectangle from graph 0,0 to graph 1,1 fillcolor rgb"#FFFFE0" behind\nset grid\nset key box\nset key opaque\n')
  
  for i in range(len(compositionDelta)):
    fo.write('\n\n\n#Scenario '+str(i)+' with probability '+str(prob[i])+'\n')
    for j in range(len(compositionDelta[i])):
      for k in range(len(compositionDelta[i][j])):
	for l in range(len(compositionDelta[i][j][k])):
	  if cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon') == 1:
	    if j == 0:
	      for m in range(location):
		if compositionTheta[i][j][k][l] == ('tM.'+str(i)+'.'+str(k)+'.'+str(m)):
		  if m < macro:
		    fo.write('#Macrocell_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers Macrocell_'+str(m)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 
		  elif m < macro + small:
		    fo.write('#Macrocell_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers Smallcell_'+str(m-macro)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 
		  elif m < location:
		    fo.write('#Macrocell_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers AP_'+str(m-macro-small)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 
	    elif j == 1:
	      for m in range(location):
		if compositionTheta[i][j][k][l] == ('tS.'+str(i)+'.'+str(k)+'.'+str(m)):
		  if m < macro:
		    fo.write('#Smallcell_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers Macrocell_'+str(m)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#), giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 
		  elif m < macro + small:
		    fo.write('#Smallcell_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers Smallcell_'+str(m-macro)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 
		  elif m < location:
		    fo.write('#Smallcell_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers AP_'+str(m-macro-small)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 	    
	    elif j == 2:
	      for m in range(location):
		if compositionTheta[i][j][k][l] == ('tA.'+str(i)+'.'+str(k)+'.'+str(m)):
		  if m < macro:
		    fo.write('#AP_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers Macrocell_'+str(m)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m]))+'\n') 
		  elif m < macro + small:
		    fo.write('#AP_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers Smallcell_'+str(m-macro)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 
		  elif m < location:
		    fo.write('#AP_'+str(k)+' has total '+str(cpx.solution.get_values(compositionBeta[j][k])/cpx.solution.get_values('psilon'))+' and covers AP_'+str(m-macro-small)+' with BW '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' for '+str(nUser[i][m])+' users\n')#, giving '+str((cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon'))*prob[i]*utility[j][k]/nUser[i][m])+'\n') 		    
    fo.write('#==============\n\n')
    
  for i in range(len(compositionTheta)):
    #fo.write('\n\n\n#Scenario '+str(i)+' with probability '+str(prob[i])+'\n')
    for j in range(len(compositionTheta[i])):
      fo.write('\n\n')
      for k in range(len(compositionTheta[i][j])):
	for l in range(len(compositionTheta[i][j][k])):
	  if j == 0:
	    for m in range(location):
	      if compositionTheta[i][j][k][l] == ('tM.'+str(i)+'.'+str(k)+'.'+str(m)) and cpx.solution.get_values(compositionNu[i][j][k][l]) == 1:
		if m < macro:
		  fo.write('Macrocell_'+str(k)+' at '+str(BigCor[k][0])+' '+str(BigCor[k][1])+' cover location_'+str(m)+' at '+str(BigCor[m][0])+' '+str(BigCor[m][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(length+25)+'\n')
		elif m < macro + small:
		  fo.write('Macrocell_'+str(k)+' at '+str(BigCor[k][0])+' '+str(BigCor[k][1])+' cover location_'+str(m)+' at '+str(SmallCor[m-macro][0])+' '+str(SmallCor[m-macro][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(rbs/space)+'\n')
		else:
		  fo.write('Macrocell_'+str(k)+' at '+str(BigCor[k][0])+' '+str(BigCor[k][1])+' cover location_'+str(m)+' at '+str(APCor[m-macro-small][0])+' '+str(APCor[m-macro-small][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(rap/space)+'\n')
	    
	  elif j == 1:
	    #fo.write('\n\n')
	    for m in range(location):
	      if compositionTheta[i][j][k][l] == ('tS.'+str(i)+'.'+str(k)+'.'+str(m)) and cpx.solution.get_values(compositionNu[i][j][k][l]) == 1:
		if m < macro:
		  fo.write('Smallcell_'+str(k)+' at '+str(SmallCor[k][0])+' '+str(Smallor[k][1])+' cover location_'+str(m)+' at '+str(BigCor[m][0])+' '+str(BigCor[m][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(length+25)+'\n')
		elif m < macro + small:
		  fo.write('Smallcell_'+str(k)+' at '+str(SmallCor[k][0])+' '+str(SmallCor[k][1])+' cover location_'+str(m)+' at '+str(SmallCor[m-macro][0])+' '+str(SmallCor[m-macro][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(rbs/space)+'\n')
		else:
		  fo.write('Smallcell_'+str(k)+' at '+str(SmallCor[k][0])+' '+str(SmallCor[k][1])+' cover location_'+str(m)+' at '+str(APCor[m-macro-small][0])+' '+str(APCor[m-macro-small][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(length+25)+'\n')
	    
	  else:
	    #fo.write('\n\n')
	    for m in range(location):
	      if compositionTheta[i][j][k][l] == ('tA.'+str(i)+'.'+str(k)+'.'+str(m)) and cpx.solution.get_values(compositionNu[i][j][k][l]) == 1:
		if m < macro:
		  fo.write('AP_'+str(k)+' at '+str(APCor[k][0])+' '+str(APCor[k][1])+' cover location_'+str(m)+' at '+str(BigCor[m][0])+' '+str(BigCor[m][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(length+25)+'\n')
		elif m < macro + small:
		  fo.write('AP_'+str(k)+' at '+str(APCor[k][0])+' '+str(APCor[k][1])+' cover location_'+str(m)+' at '+str(SmallCor[m-macro][0])+' '+str(SmallCor[m-macro][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(rbs/space)+'\n')
		else:
		  fo.write('AP_'+str(k)+' at '+str(APCor[k][0])+' '+str(APCor[k][1])+' cover location_'+str(m)+' at '+str(APCor[m-macro-small][0])+' '+str(APCor[m-macro-small][1])+' with '+str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon'))+' range '+str(rap/space)+'\n')
    fo.write('\n\n\n#Scenario '+str(i)+' with probability '+str(prob[i])+'\n')
    fo.write('#plot \''+path+'\' index '+str(4+i*3)+':'+str(4+i*3)+' using 8:9:11 notitle with labels, \''+path+'\' index '+str(4+i*3+1)+':'+str(4+i*3+1)+' using 8:9:11 notitle with labels, \''+path+'\' index '+str(4+i*3+2)+':'+str(4+i*3+2)+' using 8:9:11 notitle with labels, ')
    fo.write('\''+path+'\' index '+str(4+i*3)+':'+str(4+i*3)+' using 8:9:13 title \'Macrocells\' with circles lc rgb \'#ccffcc\' fs transparent solid 0.4 border rgb \'black\', \''+path+'\' index '+str(4+i*3+1)+':'+str(4+i*3+1)+' using 8:9:13 title \'Small cells\' with circles lc 2 lw 0.4, \''+path+'\' index '+str(4+i*3+2)+':'+str(4+i*3+2)+' using 8:9:13 title \'Hot Spots\' with circles lc 5 lw 0.4\n')
    fo.write('\n\n')
  fo.close()
  return


def scenario_prob():
  remaining_prob = 1
  for i in range(scenario):
    if i != scenario-1:
#      prob.append(round(random.uniform(0, random.uniform(0, remaining_prob*1000000))/1000000, 6))
      prob.append(round(random.uniform(0, remaining_prob)/(scenario-i), 3))
      remaining_prob -= prob[i]
    else:
      prob.append(remaining_prob)
      remaining_prob = 0
    print prob[i]
  #print prob
  return


def objective(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval):
#  for i in range(scenario):
#    for j in range(len(compositionEta[i])):
#      for k in range(len(compositionEta[i][j])):
#	for l in range(len(compositionEta[i][j][k])):
#	  tempList.append(compositionEta[i][j][k][l])
#	  for m in range(location):
#	    if compositionEta[i][j][k][l] == ('uM.'+str(i)+'.'+str(k)+'.'+str(m)):
#	      if nUser[i][m] != 0:
#		tempCoef.append(prob[i]*(float(utility[j][k])/nUser[i][m]))
#	      else:
#		tempCoef.append(0)
#	    elif compositionEta[i][j][k][l] == ('uS.'+str(i)+'.'+str(k)+'.'+str(m)):
#	      if nUser[i][m] != 0:
#		tempCoef.append(prob[i]*(float(utility[j][k])/nUser[i][m]))
#	      else:
#		tempCoef.append(0)
#	    elif compositionEta[i][j][k][l] == ('uA.'+str(i)+'.'+str(k)+'.'+str(m)):
#	      if nUser[i][m] != 0:
#		tempCoef.append(prob[i]*(float(utility[j][k])/nUser[i][m]))
#	      else:
#		tempCoef.append(0)
  #for i in range(len(compositionBeta)):
    #for j in range(len(compositionBeta[i])):
      #tempList.append(compositionBeta[i][j])
  tempList = []
  tempCoef = []
      #tempCoef.append(utility[i][j])
  for i in range(len(compositionTheta)):
    for j in range(len(compositionTheta[i])):
      for k in range(len(compositionTheta[i][j])):
	for l in range(len(compositionTheta[i][j][k])):
	  tempList.append(compositionTheta[i][j][k][l])
	  #tempList.append(compositionDelta[i][j][k][l])
	  #tempCoef.append(utility[j][k])
	  for m in range(location):
	    if compositionTheta[i][j][k][l] == 'tM.'+str(i)+'.'+str(k)+'.'+str(m):
	      tempCoef.append(nUser[scenario_set[i]][m]*prob[i]*rand_BW[scenario_set[i]][m])
	    elif compositionTheta[i][j][k][l] =='tS.'+str(i)+'.'+str(k)+'.'+str(m):
	      tempCoef.append(nUser[scenario_set[i]][m]*prob[i]*rand_BW[scenario_set[i]][m])
	    elif compositionTheta[i][j][k][l] =='tA.'+str(i)+'.'+str(k)+'.'+str(m):
	      tempCoef.append(nUser[scenario_set[i]][m]*prob[i]*rand_BW[scenario_set[i]][m])
	
  cpx.objective.set_linear(zip(tempList, tempCoef))
  del tempList
  del tempCoef
  #return


def get_utility():
  for i in range(len(utility)):
    if i == 0:
      for j in range(macro):
	utility[i].append(utiM)
    elif i == 1:
      for j in range(small):
	utility[i].append(utiS)
    elif i == 2:
      for j in range(ap):
	utility[i].append(utiA)
  print utility
  return


def correctifyConstNum(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval):
  doneRemoval = cpx.linear_constraints.get_num()
#  global constCounter
  print 'Correcting constraint numbers.....'
  constCounter = doneRemoval - 1
  for i in range(priorToRemoval, doneRemoval):
    
    astring = cpx.linear_constraints.get_names(i)
    firstPoint = astring.rfind('_')
    secondPoint = astring.find('#')
    firstPart = astring[:firstPoint]
    middlePart = astring[firstPoint:secondPoint]
    lastPart = astring[secondPoint:]
    middlePart = str(i)
    replaceStr = firstPart + middlePart + lastPart
    print replaceStr
    cpx.linear_constraints.set_names(astring, replaceStr)
  return


def constraint11(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval):
  #global constCounter
  tempList = []
  tempCoef = []
  for i in range(scenario):
    for j in range(len(compositionTheta[i])):
      for k in range(len(compositionTheta[i][j])):
	for l in range(len(compositionTheta[i][j][k])):
	  tempCoef = [1, -1, (-1)*bigM]
	  tempList = [compositionTheta[i][j][k][l], 'psilon', compositionNu[i][j][k][l]]
	  constCounter += 1
	  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [(-1)*bigM], names = ["binary(11_1)_"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)+'.'+str(l)])
	  del tempCoef[:]
	  del tempList[:]
	  tempCoef = [1, -1, bigM]
	  tempList = [compositionTheta[i][j][k][l], 'psilon', compositionNu[i][j][k][l]]
	  constCounter += 1
	  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [bigM], names = ["binary(11_2)_"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)+'.'+str(l)])
	  del tempCoef[:]
	  del tempList[:]
	  tempCoef = [1, (-1)*bigM]
	  tempList = [compositionTheta[i][j][k][l], compositionNu[i][j][k][l]]
	  constCounter += 1
	  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["binary(11_3)_"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)+'.'+str(l)])
	  del tempCoef[:]
	  del tempList[:]
  del tempList
  del tempCoef
  #return


def constraint10():
  global constCounter
  for i in range(len(compositionBeta)):
    for j in range(len(compositionBeta[i])):
#      if i == 0:
      tempList = [compositionBeta[i][j], 'psilon', compositionMu[i][j]]
      tempCoef = [1, -1, (-1)*bigM]
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [(-1)*bigM], names = ["binary(10_1)_"+str(constCounter)+"#"+str(i)])
      del tempCoef[:]
      del tempList[:]
      tempList = [compositionBeta[i][j], 'psilon', compositionMu[i][j]]
      tempCoef = [1, -1, bigM]
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [bigM], names = ["binary(10_2)_"+str(constCounter)+"#"+str(i)])
      del tempCoef[:]
      del tempList[:]
      tempList = [compositionBeta[i][j], compositionMu[i][j]]
      tempCoef = [1, (-1)*bigM]
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["binary(10_3)_"+str(constCounter)+"#"+str(i)])
      del tempCoef[:]
      del tempList[:]
#      elif i == 1:
#      elif i == 2:
  return
  

def constraint9(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval):
#  global constCounter
  tempList = []
  tempCoef = []
  for i in range(len(compositionAlpha)):
    for j in range(len(compositionAlpha[i])):
#      if i == 0:
      tempList = [compositionAlpha[i][j], 'psilon', compositionLambda[i][j]]
      tempCoef = [1, -1, (-1)*bigM]
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [(-1)*bigM], names = ["binary(9_1)_"+str(constCounter)+"#"+str(i)])
      del tempCoef[:]
      del tempList[:]
      tempList = [compositionAlpha[i][j], 'psilon', compositionLambda[i][j]]
      tempCoef = [1, -1, bigM]
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [bigM], names = ["binary(9_2)_"+str(constCounter)+"#"+str(i)])
      del tempCoef[:]
      del tempList[:]
      tempList = [compositionAlpha[i][j], compositionLambda[i][j]]
      tempCoef = [1, (-1)*bigM]
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["binary(9_3)_"+str(constCounter)+"#"+str(i)])
      del tempCoef[:]
      del tempList[:]
#      elif i == 1:
#      elif i == 2:
  del tempCoef
  del tempList
#  return


def binaryVar():
  varList = []
  for i in range(macro+small+ap):
    if i < macro:
      compositionLambda[0].append('lM'+str(i))
#      compositionMu[0].append('mM'+str(i))
    elif i < macro+small:
      compositionLambda[1].append('lS'+str(i-macro))
#      compositionMu[1].append('mS'+str(i-macro))
    else:
      compositionLambda[2].append('lA'+str(i-macro-small))
#      compositionMu[2].append('mA'+str(i-macro-small))
  for i in range(scenario):  
    compositionNu[i][0] = compositionNu[i][0] + [[] for j in range(macro)]
    compositionNu[i][1] = compositionNu[i][1] + [[] for j in range(small)]
    compositionNu[i][2] = compositionNu[i][2] + [[] for j in range(ap)]
    #for i in range(len(compositionNu[i]))
 
    for j in range(len(compositionNu[i])):
      if j == 0:
	for k in range(macro):
	  for l in range(location):
	    compositionNu[i][j][k].append('nM.'+str(i)+'.'+str(k)+'.'+str(l))
      elif j == 1:
	for k in range(small):
	  for l in range(location):
	    compositionNu[i][j][k].append('nS.'+str(i)+'.'+str(k)+'.'+str(l))
      elif j ==2:
	for k in range(ap):
	  for l in range(location):
	    compositionNu[i][j][k].append('nA.'+str(i)+'.'+str(k)+'.'+str(l))
  cpx.variables.add(names = [str(i) for i in (compositionLambda[0]+compositionLambda[1]+compositionLambda[2])], types = 'B' * (len(compositionLambda[0])+len(compositionLambda[1])+len(compositionLambda[2])))
#  cpx.variables.add(names = [str(i) for i in (compositionMu[0]+compositionMu[1]+compositionMu[2])], types = 'B' * (len(compositionMu[0])+len(compositionMu[1])+len(compositionMu[2])))
  for i in range(scenario):
    for k in range(len(compositionNu[i][0])):
      varList += compositionNu[i][0][k]
    for k in range(len(compositionNu[i][1])):
      varList += compositionNu[i][1][k]
    for k in range(len(compositionNu[i][2])):
      varList += compositionNu[i][2][k]
  cpx.variables.add(names = [str(i) for i in varList], types = 'B' * len(varList))
  del varList[:]
  return


def constraint8():
  global constCounter
  for i in range(scenario):
    for j in range(len(compositionEta[i])):
      #if j == 0:
	for k in range(len(compositionEta[i][j])):
	  for l in range(len(compositionEta[i][j][k])):
	    tempCoef = [1, (-1)*bigM]
	    tempList = [compositionEta[i][j][k][l], compositionTheta[i][j][k][l]]
	    constCounter += 1
	    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["linearize_(8_1)_"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)+'.'+str(l)])
	    del tempList[:]
	    del tempCoef[:]
	    tempCoef = [1, -1]
	    tempList = [compositionEta[i][j][k][l], compositionDelta[i][j][k][l]]
	    constCounter += 1
	    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["linearize_(8_2)_"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)+'.'+str(l)])
	    del tempCoef[:]
	    del tempList[:]
	    tempCoef = [1, -1, bigM, (-1)*bigM]
	    tempList = [compositionEta[i][j][k][l], compositionDelta[i][j][k][l], 'psilon', compositionTheta[i][j][k][l]]
	    constCounter += 1
	    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [0], names = ["linearize_(8_3)_"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)+'.'+str(l)])
	    del tempCoef[:]
	    del tempList[:]
  return


def constraint7(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval):
#  global constCounter
  tempList = []
  tempCoef = []
  for i in range(len(compositionBeta[2])):
    tempCoef = [1, -1*(Rk)]
    tempList = [compositionBeta[2][i], 'psilon']
    constCounter += 1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["AP_channel_(7)_"+str(constCounter)+"#"+str(i)])
    del tempCoef[:]
    del tempList[:]
  del tempList
  del tempCoef
#  return


def remove_duplicate_constraints(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set):
  to_remove = 0
  name_of_removal = []
  for i in range(cpx.linear_constraints.get_num()):
    for j in range(i+1, cpx.linear_constraints.get_num()):
      if str(cpx.linear_constraints.get_rows(i)) == str(cpx.linear_constraints.get_rows(j)):
	skip = 0
	
	for k in range(len(name_of_removal)):
	  if  str(cpx.linear_constraints.get_names(j)) == name_of_removal[k]:
	    
	    skip = 1
	if skip == 0:
	  to_remove += 1
	  #else:
	   # to_remove.append(str(cpx.linear_constraints.get_rows(j))
	  name_of_removal.append(cpx.linear_constraints.get_names(j))
	 # print type(cpx.linear_constraints.get_names(j))
    #print i
    
  print to_remove
  for i in range(len(name_of_removal)):
    for j in range(i+1, len(name_of_removal)):
      if name_of_removal[i] == name_of_removal[j]:
	print 'yes'
  
  for i in range(len(name_of_removal)):
   # z = cpx.linear_constraints.get_num((name_of_removal[i]))
    cpx.linear_constraints.delete(name_of_removal[i])
   # for j in range(z, cpx.linear_constraints.get.num()):
    #  cpx.linear_constraints.set_names(cpx.linear_constraints.get_names(j), "cpx.linear_constraints.get_names(j)"+'-'+str(j))
  return


def constraint6(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set):
#  global constCounter
  tempCoef = []
  tempList = []
  for i in range(macro):
    #del tempList[:]    	
    #del tempCoef[:]  
    tempList.append(compositionBeta[0][i])
    tempCoef.append(1)
    for j in range(len(neighborBig[i])):
      first_macro = tempList[:]
      first_coeff = tempCoef[:]
      first_macro.append(compositionBeta[0][neighborBig[i][j]])
      first_coeff.append(1)
      other_macro = 0	
      for k in range(len(neighborBig[neighborBig[i][j]])):
	
	if neighborBig[neighborBig[neighborBig[i][j]][k]].count(i) > 0:
	  other_macro += 1
      if other_macro == 0:
	first_macro.append('psilon')
	first_coeff.append((-1)*BW)
	constCounter += 1
	cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = first_macro, val = first_coeff)], senses = ["L"], rhs = [0], names = ["bandwidth_(6_1)_"+str(constCounter)+"#"+str(i)+'.'+str(neighborBig[i][j])])
	#print str(cplex.SparsePair(ind = first_macro, val = first_coeff))
	second_macro = first_macro[:]
	second_coeff = first_coeff[:]
	del first_macro[:]    
	del first_coeff[:] 
      else:
	for k in range(len(neighborBig[neighborBig[i][j]])):
	  third_macro = first_macro[:]
	  third_coeff = first_coeff[:]
	  second_macro = first_macro[:]
	  second_coeff = first_coeff[:]
	  if neighborBig[neighborBig[neighborBig[i][j]][k]].count(i) > 0:
	    third_macro.append(compositionBeta[0][neighborBig[neighborBig[i][j]][k]])
	    third_coeff.append(1)
	    small_cell = 0
	    for l in range(len(smallInBig[i])):
	      small_add = third_macro[:]
	      small_coe = third_coeff[:]
	      if smallCoveredBy[smallInBig[i][l]].count(neighborBig[i][j]) > 0 and smallCoveredBy[smallInBig[i][l]].count(neighborBig[neighborBig[i][j]][k]) > 0:
		small_add.append(compositionBeta[1][smallInBig[i][l]])
		small_coe.append(1)
		for m in range(len(neighborSmall[smallInBig[i][l]])):
		  small_add.append(compositionBeta[1][neighborSmall[smallInBig[i][l]][m]])
		  small_coe.append(1)
		small_cell = 1
		small_add.append('psilon')
		small_coe.append((-1)*BW)
		constCounter += 1
		cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = small_add, val = small_coe)], senses = ["L"], rhs = [0], names = ["bandwidth_(6_2)_"+str(constCounter)+"#"+str(i)+'.'+str(neighborSmall[smallInBig[i][l]][m])])
		del small_add[:]    
		del small_coe[:]
	      else:
		#for m in range(len(neighborSmall[smallInBig[i][l]])):
		 # small_add.append(compositionBeta[1][neighborSmall[smallInBig[i][l]]])
		  #small_coe.append(1)
		#small_add.append('psilon')
		#small_coe.append((-1)*BW)
		#constCounter += 1
		#cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = small_add, val = small_coe)], senses = ["L"], rhs = [0], names = ["bandwidth_(6_1)_"+str(constCounter)+"#"+str(i)])
		del small_add[:]
		del small_coe[:]
	    #else:
	    if small_cell == 0:
	      third_macro.append('psilon')
	      third_coeff.append((-1)*BW)
	      constCounter += 1
	      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = third_macro, val = third_coeff)], senses = ["L"], rhs = [0], names = ["bandwidth_(6_3)_"+str(constCounter)+"#"+str(i)+'.'+str(neighborBig[neighborBig[i][j]][k])])
	      del third_macro[:]
	      del third_coeff[:]
	  del third_coeff[:]
	  del third_macro[:]
	del first_macro[:]
	del first_coeff[:]
      for k in range(len(smallInBig[i])):
	small_add = second_macro[:]
	small_coe = second_coeff[:]
	if smallCoveredBy[smallInBig[i][k]].count(neighborBig[i][j]) > 0 and len(smallCoveredBy[smallInBig[i][k]]) < 3:
	  small_add.append(compositionBeta[1][smallInBig[i][k]])
	  small_coe.append(1)
	  for m in range(len(neighborSmall[smallInBig[i][k]])):
	    small_add.append(compositionBeta[1][neighborSmall[smallInBig[i][k]][m]])
	    small_coe.append(1)
	  small_add.append('psilon')
	  small_coe.append((-1)*BW)
	  constCounter += 1
	  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = small_add, val = small_coe)], senses = ["L"], rhs = [0], names = ["bandwidth_(6_4)_"+str(constCounter)+"#"+str(i)+'.'+str(smallInBig[i][k])])
	  del small_add[:]    
	  del small_coe[:] 
	else:
	  #small_add.append('psilon')
	  #small_coe.append((-1)*BW)
	  #constCounter += 1
	  #cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = small_add, val = small_coe)], senses = ["L"], rhs = [0], names = ["bandwidth_(6_2)_"+str(constCounter)+"#"+str(i)])
	  del small_add[:]    
	  del small_coe[:]     
      del second_coeff[:]
      del second_macro[:]
    for j in range(len(smallInBig[i])):
      small_add = tempList[:]
      small_coe = tempCoef[:]
      if len(smallCoveredBy[smallInBig[i][j]]) < 2:
	small_add.append(compositionBeta[1][smallInBig[i][j]])
	small_coe.append(1)
	for k in range(len(neighborSmall[smallInBig[i][j]])):
	  small_add.append(compositionBeta[1][neighborSmall[smallInBig[i][j]][k]])
	  small_coe.append(1)
	small_add.append('psilon')
	small_coe.append((-1)*BW)
	constCounter += 1
	cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = small_add, val = small_coe)], senses = ["L"], rhs = [0], names = ["bandwidth_(6_5)_"+str(constCounter)+"#"+str(i)+'.'+str(smallInBig[i][j])])
	del small_add[:]
	del small_coe[:]
      else:
	del small_add[:]
	del small_coe[:]
    del tempCoef[:]
    del tempList[:]
	#  for l in range(len(smallInBig[i])):
	 #   if smallCoveredBy[l].count(j) > 0 and smallCoveredBy[l].count(k) > 0:
  del tempCoef
  del tempList
#  return


def constraint4(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set):
#  global constCounter
  tempList = []
  tempCoef = []
  for i in range(scenario):
    for j in range(location):
      for k in range(len(compositionTheta[i])):
	for l in range(len(compositionTheta[i][k])):
	  for m in range(len(compositionTheta[i][k][l])):
	    if k == 0 and compositionTheta[i][k][l][m] == ('tM.'+str(i)+'.'+str(l)+'.'+str(j)):
	      tempList.append(compositionTheta[i][k][l][m])
	      tempCoef.append(1)
	    elif k == 1 and compositionTheta[i][k][l][m] == ('tS.'+str(i)+'.'+str(l)+'.'+str(j)):
	      tempList.append(compositionTheta[i][k][l][m])
	      tempCoef.append(1)
	    elif k == 2 and compositionTheta[i][k][l][m] == ('tA.'+str(i)+'.'+str(l)+'.'+str(j)):
	      tempList.append(compositionTheta[i][k][l][m])
	      tempCoef.append(1)
      tempList.append('psilon')
      tempCoef.append(-1)
      
      constCounter += 1
      cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["L"], rhs = [0], names = ["location_(4)_"+str(constCounter)+"#"+str(i)+'.'+str(j)])
      del tempList[:]    
      del tempCoef[:]
  del tempList
  del tempCoef
#  return
  
 
def update(index_of_removal, column, row, matrix, reduced_scenario):
#  print matrix
#  print column
#  print row
#  tempV = 0
  for i in range(len(column)):
    matrix[i].pop(index_of_removal)
#    print matrix
  del matrix[index_of_removal]
  column.pop(index_of_removal)
  row.pop(index_of_removal)
  
#  print column
#  print row
  for i in range(len(column)):
    for j in range(len(row)):
      if cmp((abs(row[j]-column[i])), (abs(row[j]-reduced_scenario[-1]))) == 1:
	matrix[j][i] = abs(row[j]-reduced_scenario[-1])
      elif cmp((abs(row[j]-column[i])), (abs(row[j]-reduced_scenario[-1]))) == -1:
	matrix[j][i] = abs(row[j]-column[i])
      elif cmp((abs(row[j]-column[i])), (abs(row[j]-reduced_scenario[-1]))) == 0:
	matrix[j][i] = abs(row[j]-column[i])
  print matrix
  return


def scenario_generation(reduced_scenario_number):
  reduced_scenario_prob = []
  reduced_scenario = []
  if reduced_scenario_number != scenario:
#    set_of_removal = []
  #  reduced_scenario_number = int(math.ceil(((location*scenario)+1.0)/(location+1.0)))
    #scenario_mean = []
  #  scenario_total = 0.0
  #  for i in range(location):
  #    scenario_total = 0.0
  #    for j in range(scenario):
  #      scenario_total += nUser[j][i]
  #    scenario_mean.append(scenario_total/scenario)
  #    
  #  quad = cplex.Cplex()
  #  print reduced_scenario_number
  #  reduced_variable = []
  #  for i in range(reduced_scenario_number):
  #    reduced_variable.append('w'+str(i))
  #  print reduced_variable
  #  quad.
    row = [i for i in range(scenario)] 
    column = [j for j in range(scenario)]
    matrix = [[] for i in range(scenario)]
    for i in range(scenario):
      for j in range(scenario):
	matrix[i].append(abs(i-j))
    print matrix
    #print reduced_scenario
    summation = [0.0 for i in range(scenario)]
    #print prob
    for i in range(len(column)):
      for j in range(len(row)):
	summation[i] += matrix[j][i]*prob[row[j]]
	#print prob[column[i]]
	#print matrix[j][i]
    #print 'step 1:'
    print summation
    #del summation[:]
    #set_of_removal.append(column[summation.index(min(summation))])
    reduced_scenario.append(column[summation.index(min(summation))])
    print reduced_scenario
    update(summation.index(min(summation)), column, row, matrix, reduced_scenario)
    del summation[:]
    #summation.pop()
    h = 0
    while h < reduced_scenario_number - 1:
      for i in range(len(column)):
	summation.append(0.0)
	for j in range(len(row)):
	  summation[i] += matrix[j][i]*prob[row[j]]
      print summation
      reduced_scenario.append(column[summation.index(min(summation))])
      print reduced_scenario
      update(summation.index(min(summation)), column, row, matrix, reduced_scenario)
      del summation[:]
#      summation.pop()
      h += 1
    reduced_scenario.sort()  
#    for i in range(scenario):
      #for j in range(len(set_of_removal)):
#      if set_of_removal.count(i) == 0:
    for i in range(len(reduced_scenario)):
      reduced_scenario_prob.append(prob[reduced_scenario[i]])
      if reduced_scenario[i] <= scenario - reduced_scenario[i]:
	for j in range(1, scenario - reduced_scenario[i]):
	  
	  if (reduced_scenario.count(reduced_scenario[i]+j) == 0 or reduced_scenario.count(reduced_scenario[i]-j) == 0):
	    
	    if reduced_scenario.count(reduced_scenario[i]+j) == 0 and reduced_scenario[i]+j < scenario:
	      reduced_scenario_prob[i] += prob[reduced_scenario[i]+j]
	    if reduced_scenario.count(reduced_scenario[i]-j) == 0 and reduced_scenario[i]-j >= 0:
	      reduced_scenario_prob[i] += prob[reduced_scenario[i]-j]
	    if reduced_scenario_prob[i] > prob[reduced_scenario[i]]:
	      break
	    
      else: 
	for j in range(1, reduced_scenario[i]):
	  if reduced_scenario.count(reduced_scenario[i]+j) == 0 or reduced_scenario.count(reduced_scenario[i]-j) == 0:
	    if reduced_scenario[i]+j < scenario and reduced_scenario.count(reduced_scenario[i]+j) == 0:
	      reduced_scenario_prob[i] += prob[reduced_scenario[i]+j]
	    if reduced_scenario[i]-j >= 0 and reduced_scenario.count(reduced_scenario[i]-j) == 0:
	      reduced_scenario_prob[i] += prob[reduced_scenario[i]-j]
	    if reduced_scenario_prob[i] > prob[reduced_scenario[i]]:
	      break
  return reduced_scenario_prob, reduced_scenario


def scenarioUserNum(reduced_scenario_number):
  for i in range(scenario):
    y, z = locUserNum()
    print z
    print y
    for j in range(len(z)):
      nUser[i].append(z[j])
      rand_BW[i].append(y[j])
    #print 'user numbers for scenario '+str(i)+' added!'
  #print nUser
  for i in range(len(reduced_scenario_number)):
    preserved_scenario_prob[i], preserved_scenario[i] = scenario_generation(reduced_scenario_number[i])  
  return
  
  
def constraint5(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set):
#  global constCounter
  #print tempList
  #print tempCoef
  tempList = []
  tempCoef = []
  for i in range(len(compositionAlpha[0])):
    tempList.append(compositionAlpha[0][i])
    tempList.append(compositionBeta[0][i])
    constCounter += 1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [1, -1])], senses = ["L"], rhs = [0], names = ["operation_(5_1)"+str(constCounter)+"#"+str(i)])
    constCounter += 1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [bigM, -1])], senses = ["G"], rhs = [0], names = ["operation_(5_2)"+str(constCounter)+"#"+str(i)])
    del tempList[:]
    del tempCoef[:]
  for i in range(len(compositionAlpha[1])):
    tempList.append(compositionAlpha[1][i])
    tempList.append(compositionBeta[1][i])
    constCounter += 1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [1, -1])], senses = ["L"], rhs = [0], names = ["operation_(5_1)"+str(constCounter)+"#"+str(i)])
    constCounter += 1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [bigM, -1])], senses = ["G"], rhs = [0], names = ["operation_(5_2)"+str(constCounter)+"#"+str(i)])
    
    del tempList[:]
    del tempCoef[:]
  for i in range(len(compositionAlpha[2])):
    tempList.append(compositionAlpha[2][i])
    tempList.append(compositionBeta[2][i])
    constCounter += 1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [1, -1])], senses = ["L"], rhs = [0], names = ["operation_(5_1)"+str(constCounter)+"#"+str(i)])
    constCounter += 1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [bigM, -1])], senses = ["G"], rhs = [0], names = ["operation_(5_2)"+str(constCounter)+"#"+str(i)])
    del tempList[:]
    del tempCoef[:]
    
  for i in range(scenario):
    for j in range(len(compositionDelta[i])):
      for k in range(len(compositionDelta[i][j])):
	for l in range(len(compositionDelta[i][j][k])):
	  tempList.append(compositionTheta[i][j][k][l])
	  tempList.append(compositionDelta[i][j][k][l])
	  constCounter += 1
	  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [1, -1])], senses = ["L"], rhs = [0], names = ["operation_(5_1)"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)])
	  constCounter += 1
	  cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = [bigM, -1])], senses = ["G"], rhs = [0], names = ["operation_(5_2)"+str(constCounter)+"#"+str(i)+'.'+str(j)+'.'+str(k)])
	  del tempList[:]
	  del tempCoef[:]
  del tempCoef
  del tempList
#  return
  
  
def constraint3(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set):
#  global constCounter
  tempList = []
  tempCoef = []
  for i in range(scenario):
    #del tempList[:]
   # del tempCoef[:]
    for j in range(len(compositionTheta)):
      if j == 0:
	for k in range(len(compositionTheta[i][0])):
	  for l in range(len(compositionTheta[i][0][k])):
	    for m in range(location):
	      if compositionTheta[i][0][k][l] == ('tM.'+str(i)+'.'+str(k)+'.'+str(m)):
		tempList.append(compositionTheta[i][0][k][l])
		tempCoef.append(nUser[scenario_set[i]][m])
      elif j == 1:
	for k in range(len(compositionTheta[i][1])):
	  for l in range(len(compositionTheta[i][1][k])):
	    for m in range(location):
	      if compositionTheta[i][1][k][l] == ('tS.'+str(i)+'.'+str(k)+'.'+str(m)):
		tempList.append(compositionTheta[i][1][k][l])
		tempCoef.append(nUser[scenario_set[i]][m])	
      elif j ==2:
	for k in range(len(compositionTheta[i][2])):
	  for l in range(len(compositionTheta[i][2][k])):
	    for m in range(location):
	      if compositionTheta[i][2][k][l] == ('tA.'+str(i)+'.'+str(k)+'.'+str(m)):
		tempList.append(compositionTheta[i][2][k][l])
		tempCoef.append(nUser[scenario_set[i]][m])	
    tempList.append('psilon')
    tempCoef.append(Ntp[scenario_set[i]]*(1-BP)*(-1))
   
    constCounter+=1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["G"], rhs = [0], names = ["BP_(3)_"+str(constCounter)+"#"+str(i)])
    del tempList[:]
    del tempCoef[:]
  del tempCoef
  del tempList
  #return
  
  
def locUserNum():
  Ntp.append(randrange(min_user, max_user+1))
  
  y = []
  for i in range(location):
    y.append(random.uniform(min_BW, max_BW))
    
  userCor = [[0.0 for col in range(2)] for row in range(Ntp[-1])] 
  userNumAtLoc = [0 for i in range(location)]
  i = 0
  while i < Ntp[-1]:
    ShortestDistance = 10000000
    sameLoc = 0
    if i <= Ntp[-1]*UrbanUser:
      userCor[i][0] = random.randint(X1urban, X2urban+1)
      userCor[i][1] = random.randint(Y1urban, Y2urban+1)
    elif i <= Ntp[-1]*(UrbanUser+SubUser):
      userCor[i][0] = random.randint(X1suburban, X2suburban+1)
      userCor[i][1] = random.randint(Y1suburban, Y2suburban+1)      
    else:
      userCor[i][0] = random.randint(0, Px+1)
      userCor[i][1] = random.randint(0, Py+1)
      
    for j in range(macro):
      tempDistance = space*distance(BigCor[j], userCor[i])
      if tempDistance < ShortestDistance:
	ShortestDistance=tempDistance
	
    if ShortestDistance > Rbs + 25*space:
      i = i - 1
    else:
      for j in range(macro):
	if BigCor[j][0] == userCor[i][0] and BigCor[j][1] == userCor[i][1]:
	  i = i - 1
	  sameLoc = 1
	  break
      for j in range(small):
	if SmallCor[j][0] == userCor[i][0] and SmallCor[j][1] == userCor[i][1] and sameLoc == 0:
	  i = i - 1
	  sameLoc = 1
	  break
      for j in range(ap):
	if APCor[j][0] == userCor[i][0] and APCor[j][1] == userCor[i][1] and sameLoc == 0:
	  i -= 1
	  break
    i = i + 1

  for j in range(Ntp[-1]):
    ShortestDistance = 1000000
    userLoc = -1
    for i in range(location):
      if i < macro:
	if distance(BigCor[i], userCor[j]) < ShortestDistance and space * distance(BigCor[i], userCor[j]) <= Rbs + 25*space:
	  ShortestDistance = distance(BigCor[i], userCor[j])
	  userLoc = i
#	  userNumAtLoc[i] += 1
      elif i < macro + small:
	if distance(SmallCor[i-macro], userCor[j]) < ShortestDistance and space * distance(SmallCor[i-macro], userCor[j]) <= rbs:
	  ShortestDistance = distance(SmallCor[i-macro], userCor[j])
	  userLoc = i
#	  userNumAtLoc[i] += 1
      else:
	if distance(APCor[i-macro-small], userCor[j]) < ShortestDistance and space * distance(APCor[i-macro-small], userCor[j]) <= rap:
	  ShortestDistance = distance(APCor[i-macro-small], userCor[j])
	  userLoc = i
    userNumAtLoc[userLoc] += 1
    #print str(j)+' in '+str(i)+' with distance of '+str(ShortestDistance)
#      else:
#	print 'error!'
#	sys.exit(1)
#  for j in range(Ntp):
#    for i in range(location):
#      if i < macro:
#	if space * distance(BigCor[i], userCor[j]) <= Rbs + 25*space:
#	  userNumAtLoc[i] += 1
#      elif i < macro + small:
#	if space * distance(SmallCor[i-macro], userCor[j]) <= rbs:
#	  userNumAtLoc[i] += 1
#      elif i < location:
#	if space * distance(APCor[i-macro-small], userCor[j]) <= rap:
#	  userNumAtLoc[i] += 1
    
  #print userNumAtLoc
  return y, userNumAtLoc
  

BW = 30
macroActP = 500
macroSleP = 8
smallActP = 3.66
smallSleP = 0.96
apActP = 2.79
apSleP = 0.028
BP = 0.07

map_x = 50000.0
map_y = 50000.0

min_BW = 0.161
max_BW = 0.253
min_user = 910
max_user = 2300
space = 20.0
Rbs = 5000.0
rbs = 1100.0
rap = 600.0
utiM = 6.6
utiS = 9.2
utiA = 13.7

X1urban = 750.0
X2urban = 1500.0
Y1urban = 750.0
Y2urban = 1500.0
X1suburban = 500.0
X2suburban = 1750.0
Y1suburban = 500.0
Y2suburban = 1750.0

UrbanUser = 0.0
SubUser = 0.0
RuralUser = 1
UrbanSmall = 0.0
SubSmall = 0.0
RuralSmall = 1
UrbanAP= 0.0
SubAP = 0.0
RuralAP = 1

bigM = 10000
constCounter = 0
Rk = 1

addMacroEne = 2.02
addSmallEne = 1.52
addAPEne = 0.95

scenario = 780
preserved_scenario_number = [290, 190]
small = 21
ap = 26

Gbs_x = map_x/Rbs
Gbs_y = map_y/Rbs
Nbs_x1 = math.floor ( ( Gbs_x-2 ) / 3 ) + 1
Nbs_x2 = math.floor ( ( ( map_x - ( Rbs / 2 ) ) /Rbs ) / 3 )
Nbs_y1 = math.floor ( Gbs_y / 2 )
Nbs_y2 = math.floor ( ( ( map_y - Rbs ) / Rbs ) / 2 )
if Nbs_x1 < 1 or Nbs_x2 < 1 or Nbs_y1 < 1 or Nbs_y2 < 1:
  print ('Initial Map Error. Program Stops!')
  sys.exit(1)


macro = int((Nbs_x1 * Nbs_y1) + (Nbs_x2 * Nbs_y2))
#print macro
length = Rbs/space
Px = map_x/space
Py = map_y/space

Tbs = macro + small
location = macro + small + ap

nUser = [[] for i in range(scenario)]
BigCor = [ [0.0 for col in range(2)] for row in range(macro) ]
SmallCor = [ [0.0 for col in range(2)] for row in range(small) ]
APCor = [ [0.0 for col in range(2)] for row in range(ap) ]

smallInBig = [[] for i in range(macro)]
apInBig = [[] for i in range(macro)]
apInSmall = [[] for i in range(small)]
smallCoveredBy = [[] for i in range(small)]
apCoveredBy = [[] for i in range(ap)]
apCoveredBySmall = [[] for i in range(ap)]

neighborBig = [[] for i in range(macro)]
neighborSmall = [[] for i in range(small)]
neighborAP = [[] for i in range(ap)]

utility = [[] for i in range(3)]
prob = []
preserved_scenario = [[] for i in range(len(preserved_scenario_number))] 
preserved_scenario_prob = [[] for i in range(len(preserved_scenario_number))]
Ntp = []
scenario_set = [i for i in range(scenario)]
rand_BW = [[] for i in range(scenario)]
  
  
def drange(start, stop, step):
  r = start
  while r < stop:
    yield r
    r += step
  
  
def station_coordinate():
  Sx = Sy = 1
  Zy = Nbs_x1
  Ay = Nbs_x1
  By = Nbs_x2
  Zx = Nbs_y1
  Ax = Nbs_y1
  Bx = Nbs_y2
  m = tBS = 0
  #tDistance = 0.0
  #sDistance = 1000000000;
  
  for j in drange(1, (Gbs_y-1)+1, 1):
    for i in drange(Sy, Zy+1, 1):
      BigCor[int(i-1)].pop(1)
      BigCor[int(i-1)].append(j*length)
    Sy = Zy + 1
    if j%2 == 1:
      Zy += By
    else:
      Zy += Ay
      
  for m in drange(1, (Gbs_x-1)+1, 1.5):
    for l in drange(Sx, (Sx+(Ay+By)*(Zx-1))+1, Ay+By):
      BigCor[int(l-1)].pop(0)
      BigCor[int(l-1)].insert(0, m*length)
    if (int(m+2))%3 == 0:
      Sx += Ay
      Zx = Bx
    else:
      Sx = Sx - Ay + 1
      Zx= Ax
      
  tempDistance = [0.0 for row in range(macro)]
  i = 0
  while i < small:
    sameLoc = 0
    ShortestDistance = 10000000.0
    #for m in range(0, small):
    if i <= small * UrbanSmall:
      SmallCor[i][0] =  random.randint(X1urban, X2urban+1)
      SmallCor[i][1] =  random.randint(Y1urban, Y2urban+1)
    elif i <= small*(UrbanSmall+SubSmall):
      SmallCor[i][0] =  random.randint(X1suburban, X2suburban+1)
      SmallCor[i][1] =  random.randint(Y1suburban, Y2suburban+1)
    else:
      SmallCor[i][0] =  random.randint(0, Px+1)
      SmallCor[i][1] =  random.randint(0, Py+1)
    for k in range(0, macro):
      if BigCor[k][0] == SmallCor[i][0] and BigCor[k][1] == SmallCor[i][1]:
	i = i - 1
	sameLoc = 1
    if sameLoc == 0:
      for n in range(0, macro):
	tempDistance[n] = space*distance(BigCor[n], SmallCor[i])
	if tempDistance[n] < ShortestDistance:
	  ShortestDistance = tempDistance[n]
	#print str(i)+' '+str(n)+' '+str(ShortestDistance)
      #print Rbs
      if ShortestDistance + rbs > Rbs + 25*space:
	#print 'renew'
	i = i - 1
	sameLoc = 1
    if sameLoc == 0:
      for o in range(i-1, -1, -1):
	if SmallCor[i][0] == SmallCor[o][0] and SmallCor[i][1] == SmallCor[o][1]:
	  i = i - 1
	  sameLoc = 1
    if sameLoc == 0:
      distanceToS = 0.0
      for p in range(0, macro):
	distanceToS = space*distance(BigCor[p], SmallCor[i])
	if (distanceToS < Rbs + 25*space and distanceToS + rbs > Rbs + 25*space) or (distanceToS > Rbs + 25*space and distanceToS -rbs < Rbs + 25*space):
	  i = i - 1
	  #sameLoc = 1
	  break
    i += 1
    
  i = 0
  while i < ap:
    sameLoc = 0
    ShortestDistance = 10000000.0
   # for m in range(0, ap):
    if i <= small * UrbanAP:
      APCor[i][0] =  random.randint(X1urban, X2urban+1)
      APCor[i][1] =  random.randint(Y1urban, Y2urban+1)
    elif i <= small*(UrbanAP+SubAP):
      APCor[i][0] =  random.randint(X1suburban, X2suburban+1)
      APCor[i][1] =  random.randint(Y1suburban, Y2suburban+1)
    else:
      APCor[i][0] =  random.randint(0, Px+1)
      APCor[i][1] =  random.randint(0, Py+1)
    for k in range(0, macro):
      if BigCor[k][0] == APCor[i][0] and BigCor[k][1] == APCor[i][1]:
	i = i - 1
	sameLoc = 1
    if sameLoc == 0:
      for j in range(0, small):
	if SmallCor[j][0] == APCor[i][0] and SmallCor[j][1] == APCor[i][1]:
	  i = i-1
	  sameLoc = 1
    if sameLoc == 0:
      for l in range(i-1, -1, -1):
	if APCor[l][0] == APCor[i][0] and APCor[l][1] == APCor[i][1]:
	  i = i-1
	  sameLoc = 1
    if sameLoc == 0:
      for n in range(0, macro):
	tempDistance[n] = space*distance(BigCor[n], APCor[i])
	if tempDistance[n] < ShortestDistance:
	  ShortestDistance = tempDistance[n]
      if ShortestDistance + rap > Rbs + 25*space:
	i = i - 1
	sameLoc = 1
    if sameLoc == 0:
      distanceToS = 0.0
      for p in range(0, small):
	distanceToS = space*distance(SmallCor[p], APCor[i])
	if (distanceToS < rbs and distanceToS + rap > rbs) or (distanceToS > rbs and distanceToS -rap < rbs):
	  i = i - 1
	  sameLoc = 1
	  break
    if sameLoc == 0:
      distanceToS = 0.0
      for p in range(0, macro):
	distanceToS = space*distance(BigCor[p], APCor[i])
	if (distanceToS < Rbs + 25*space and distanceToS + rap > Rbs + 25*space) or (distanceToS > Rbs + 25*space and distanceToS -rap < Rbs + 25*space):
	  i = i - 1
	  #sameLoc = 1
	  break
#    if sameLoc == 0:
#      ShortestDistance = 1000000.0
#      tempDistance = 0.0
#      for p in range(0, small):
#	tempDistance = space*distance(SmallCor[p], APCor[i])
#	if tempDistance < ShortestDistance:
#	  ShortestDistance = tempDistance
#      if ShortestDistance - rap < rbs and (ShortestDistance > rbs or ShortestDistance + rap > rbs):
#	i = i - 1
#	sameLoc == 1
#    if sameLoc == 0:
#      ShortestDistance = 1000000.0
#      tempDistance = 0.0
#      for p in range(0, macro):
#	tempDistance = space*distance(BigCor[p], APCor[i])
#	if tempDistance < ShortestDistance:
#	  ShortestDistance = tempDistance
#      if ShortestDistance - rap < Rbs and (ShortestDistance > Rbs or ShortestDistance + rap > Rbs):
#	i = i - 1
    i += 1
	
  return


def output_userDistr():
  
  path = "../setupInfo/station coordinates.txt"
  f = open(path, 'a')
  f.write('#The following information is on the user numbers at each location for scenarios.\n')
  averLocUser = []  
  largestUserNum = 0
  for i in range(len(nUser)):
    f.write( 'Scenario '+str(i)+'\n')
      #averLocUser
    for j in range(len(nUser[i])):
      #print len(nUser[i])
      if i == 0:
	averLocUser.append(0)
      if j < macro:
	f.write('#Macrocell '+str(j)+' has '+str(nUser[i][j])+' users.\n')
	averLocUser[j] += prob[i]*nUser[i][j]
	if i == len(nUser)-1 and largestUserNum < averLocUser[j]:
	  largestUserNum = averLocUser[j]
      elif j < macro + small:
	f.write('#Small cell '+str(j-macro)+' has '+str(nUser[i][j])+' users.\n')
	averLocUser[j] += prob[i]*nUser[i][j]
	if i == len(nUser)-1 and largestUserNum < averLocUser[j]:
	  largestUserNum = averLocUser[j]
      else:
	f.write('#Access point '+str(j-macro-small)+' has '+str(nUser[i][j])+' users.\n')
	averLocUser[j] += prob[i]*nUser[i][j]
	if i == len(nUser)-1 and largestUserNum < averLocUser[j]:
	  largestUserNum = averLocUser[j]
    f.write('#===============\n')
  
  f.write('\n\n#The following information is on the expected user numbers at each location.\n')
  for i in range(len(averLocUser)):
          #if i == 0:
	#averLocUser[j] = 0
    if i < macro:
      f.write('Macrocell_'+str(i)+': '+str(BigCor[i][0])+' '+str(BigCor[i][1])+' '+str(length+25)+' '+str(averLocUser[i])+' '+str(averLocUser[i]/largestUserNum)+'\n\n\n')
	#averLocUser[j] += prob[i]*nUser[i][j]
    elif i < macro + small:
      f.write('SmallCell_'+str(i-macro)+': '+str(SmallCor[i-macro][0])+' '+str(SmallCor[i-macro][1])+' '+str(rbs/space)+' '+str(averLocUser[i])+' '+str(averLocUser[i]/largestUserNum)+'\n\n\n')
	#averLocUser[j] += prob[i]*nUser[i][j]
    else:	
      f.write('AccessPoint_'+str(i-macro-small)+': '+str(APCor[i-macro-small][0])+' '+str(APCor[i-macro-small][1])+' '+str(rap/space)+' '+str(averLocUser[i])+' '+str(averLocUser[i]/largestUserNum)+'\n\n\n')
	#averLocUser[j] += prob[i]*nUser[i][j]
    #f.write('===============\n\n')  
    
  f.write('\n\n#The following is the input to gnuplot to generate a figure of user density.\n')
  #f.write('\nplot \''+path+'\' index 0:0 using 2:3:4 title \'Macrocells\' with circles lc rgb \'#ccffcc\' fs transparent solid 0.4 border rgb \'black\', \''+path+'\' index 1:1 using 2:3:4 title \'Small cells\' with circles lc 2 lw 0.4, \''+path+'\' index 2:2 using 2:3:4 title \'Hot Spots\' with circles lc 5 lw 0.4, \''+path+'\' index 0:0 using 2:3:4 title \'Macrocell BSs\' with points lc 0, \''+path+'\' index 1:1 using 2:3:4 title \'Small cell BSs\' with points lc 8 ps 0.6, \''+path+'\' index 2:2 using 2:3:4 title \'APs\' with points lc 4 ps 0.6 pt 3\n')
  f.write('set size square\nset xrange[-50:2150]\nset yrange[-50:2150]\nset object 1 rectangle from graph 0,0 to graph 1,1 fillcolor rgb"#FFFFE0" behind\nset grid\nset key box\nset key opaque')
  f.write('\nplot')
  for i in range(len(averLocUser)):
    if i < macro:
      f.write('\''+path+'\' index '+str(4+i)+':'+str(4+i)+' using 2:3:4 notitle with circles lc rgb "#000000" fs transparent solid '+str(1-(averLocUser[i]/largestUserNum))+' border rgb "#B0C4DE", ')
    elif i <macro + small:
      f.write('\''+path+'\' index '+str(4+i)+':'+str(4+i)+' using 2:3:4 notitle with circles lc rgb "#90EE90" fs transparent solid '+str(1-(averLocUser[i]/largestUserNum))+' border rgb "#B0C4DE", ')
    else:
      f.write('\''+path+'\' index '+str(4+i)+':'+str(4+i)+' using 2:3:4 notitle with circles lc rgb "#778899" fs transparent solid '+str(1-(averLocUser[i]/largestUserNum))+' border rgb "#B0C4DE", ')
  f.write('\''+path+'\' index 0:0 using 2:3:4 title \'Macrocell BSs\' with points lc 0, \''+path+'\' index 1:1 using 2:3:4 title \'Small cell BSs\' with points lc 8 ps 0.6, \''+path+'\' index 2:2 using 2:3:4 title \'APs\' with points lc 4 ps 0.6 pt 3\n')
  f.close()
  
  return

  
def output_coordinate_information(corToPrint, staType):
  path = "../setupInfo/station coordinates.txt"
  
  #print f
  if staType == 'macrocell Coordinate':
    f = open(path,'w')
    f.write('#This file lists the coordinates of stations.\n\n')
    f.write('#The following is about '+staType+'\n')
    for i in range(macro):
      f.write('MC_'+str(i)+': '+str(int(corToPrint[i][0]))+' '+str(int(corToPrint[i][1]))+' '+str(length+25)+'\n')
    f.write('\n\n')
  else:
    f = open(path,'a')
    f.write('\n\n#The following is about '+staType+'.\n')
    if staType == 'small cell Coordinate':
      for i in range(small):
	f.write('SC_'+str(i)+': '+str(corToPrint[i][0])+' '+str(corToPrint[i][1])+' '+str(rbs/space)+'\n')
    else:
      for i in range(ap):
	f.write('AP_'+str(i)+': '+str(corToPrint[i][0])+' '+str(corToPrint[i][1])+' ' +str(rap/space)+'\n')
      f.write('\nplot \''+path+'\' index 0:0 using 2:3:4 title \'Macrocells\' with circles lc rgb \'#ccffcc\' fs transparent solid 0.4 border rgb \'black\', \''+path+'\' index 1:1 using 2:3:4 title \'Small cells\' with circles lc 2 lw 0.4, \''+path+'\' index 2:2 using 2:3:4 title \'Hot Spots\' with circles lc 5 lw 0.4, \''+path+'\' index 0:0 using 2:3:4 title \'Macrocell BSs\' with points lc 0, \''+path+'\' index 1:1 using 2:3:4 title \'Small cell BSs\' with points lc 8 ps 0.6, \''+path+'\' index 2:2 using 2:3:4 title \'APs\' with points lc 4 ps 0.6 pt 3\n')
      f.write('set size square\nset xrange[-100:2100]\nset yrange[-400:1800]\nset key box\nset key maxrows 3\nset object 1 rectangle from graph 0,0 to graph 1,1 fillcolor rgb"#ffcccc" behind\nset key opaque\nset key bottom left\nset grid\n')
      #f.write('replot')
    f.write('\n\n')
    
 
  
  f.close()
  return


def station_covered_in():

  for i in range(macro):
    for j in range(small):
      if space*distance(BigCor[i], SmallCor[j]) + rbs <= Rbs + 25*space:
	smallInBig[i].append(j)
	smallCoveredBy[j].append(i)
     
    for k in range(ap):
      if space*distance(BigCor[i], APCor[k]) + rap <= Rbs + 25*space:
	apInBig[i].append(k)
	apCoveredBy[k].append(i)
	
  for j in range(small):
    for l in range(ap):
	if space*distance(SmallCor[j], APCor[l]) + rap <= rbs:
	  apInSmall[j].append(l)
	  apCoveredBySmall[l].append(j)
  return
  
  
def station_neighbor():

  for i in range(0, macro):
    for j in range(i+1, macro):
      if space*distance(BigCor[i], BigCor[j]) <= Rbs*2:
	neighborBig[i].append(j)
	neighborBig[j].append(i)
  for i in range(0, small):
    for j in range(i+1, small):
      if space*distance(SmallCor[i], SmallCor[j]) <= rbs*2:
	neighborSmall[i].append(j)
	neighborSmall[j].append(i)
  for i in range(0, ap):
    for j in range(i+1, ap):
      if space*distance(APCor[i], APCor[j]) <= rap*2:
	neighborAP[i].append(j)
	neighborAP[j].append(i)
	
  return


def delete(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter):
  for i in range(small):
    for j in range(macro):
      if smallCoveredBy[i].count(j) == 0:
	for k in range(scenario):
	  #for l in range(location):
	  cpx.variables.delete(compositionDelta[k][0][j][macro+i])
#	  cpx.variables.delete(compositionEta[k][0][j][macro+i])
	  cpx.variables.delete(compositionTheta[k][0][j][macro+i])
	  cpx.variables.delete(compositionNu[k][0][j][macro+i])
#	  compositionDelta[k][0][j].remove(compositionDelta[k][0][j][macro+i])
#	  compositionEta[k][0][j].remove(compositionEta[k][0][j][macro+i])
#	  compositionTheta[k][0][j].remove(compositionTheta[k][0][j][macro+i])
  for i in range(ap):
    for j in range(macro):
      if apCoveredBy[i].count(j) == 0:
	for k in range(scenario):
	  #for l in range(location):
	  cpx.variables.delete(compositionDelta[k][0][j][macro+small+i])
#	  cpx.variables.delete(compositionEta[k][0][j][macro+small+i])
	  cpx.variables.delete(compositionTheta[k][0][j][macro+small+i])
	  cpx.variables.delete(compositionNu[k][0][j][macro+small+i])
#	  compositionDelta[k][0][j].remove(compositionDelta[k][0][j][macro+small+i])
#	  compositionEta[k][0][j].remove(compositionEta[k][0][j][macro+small+i])
#	  compositionTheta[k][0][j].remove(compositionTheta[k][0][j][macro+small+i])	  
  for i in range(ap):
    for j in range(small):
      if apCoveredBySmall[i].count(j) == 0:
	for k in range(scenario):
	  #for l in range(location):
	  cpx.variables.delete(compositionDelta[k][1][j][macro+small+i])
#	  cpx.variables.delete(compositionEta[k][1][j][macro+small+i])
	  cpx.variables.delete(compositionTheta[k][1][j][macro+small+i])
	  cpx.variables.delete(compositionNu[k][1][j][macro+small+i])
#	  compositionDelta[k][1][j].remove(compositionDelta[k][1][j][macro+small+i])
#	  compositionEta[k][1][j].remove(compositionEta[k][1][j][macro+small+i])
#	  compositionTheta[k][1][j].remove(compositionTheta[k][1][j][macro+small+i])	  
  for i in range(macro):
    for j in range(macro):
      if i != j:
	for k in range(scenario):
	  cpx.variables.delete(compositionDelta[k][0][i][j])
#	  cpx.variables.delete(compositionEta[k][0][i][j])
	  cpx.variables.delete(compositionTheta[k][0][i][j])
	  cpx.variables.delete(compositionNu[k][0][i][j])
#	  compositionDelta[k][0][i].remove(compositionDelta[k][0][i][j])
#	  compositionEta[k][0][i].remove(compositionEta[k][0][i][j])
#	  compositionTheta[k][0][i].remove(compositionTheta[k][0][i][j])	  
  for i in range(small):
    for j in range(macro):
      for k in range(scenario):
	cpx.variables.delete(compositionDelta[k][1][i][j])
#	cpx.variables.delete(compositionEta[k][1][i][j])
	cpx.variables.delete(compositionTheta[k][1][i][j])
	cpx.variables.delete(compositionNu[k][1][i][j])
#	compositionDelta[k][1][i].remove(compositionDelta[k][1][i][j])
#	compositionEta[k][1][i].remove(compositionEta[k][1][i][j])
#	compositionTheta[k][1][i].remove(compositionTheta[k][1][i][j])	
    for j in range(small):
      if i != j:
	for k in range(scenario):
	  cpx.variables.delete(compositionDelta[k][1][i][macro+j])
#	  cpx.variables.delete(compositionEta[k][1][i][macro+j])
	  cpx.variables.delete(compositionTheta[k][1][i][macro+j])
	  cpx.variables.delete(compositionNu[k][1][i][macro+j])
#	  compositionDelta[k][1][i].remove(compositionDelta[k][1][i][macro+j])
#	  compositionEta[k][1][i].remove(compositionEta[k][1][i][macro+j])
#	  compositionTheta[k][1][i].remove(compositionTheta[k][1][i][macro+j])	  
  for i in range(ap):
    for j in range(macro):
      for k in range(scenario):
	cpx.variables.delete(compositionDelta[k][2][i][j])
#	cpx.variables.delete(compositionEta[k][2][i][j])
	cpx.variables.delete(compositionTheta[k][2][i][j])
	cpx.variables.delete(compositionNu[k][2][i][j])
#	compositionDelta[k][2][i].remove(compositionDelta[k][2][i][j])
#	compositionEta[k][2][i].remove(compositionEta[k][2][i][j])
#	compositionTheta[k][2][i].remove(compositionTheta[k][2][i][j])	
    for j in range(small):
      for k in range(scenario):
	cpx.variables.delete(compositionDelta[k][2][i][macro+j])
#	cpx.variables.delete(compositionEta[k][2][i][macro+j])
	cpx.variables.delete(compositionTheta[k][2][i][macro+j])
	cpx.variables.delete(compositionNu[k][2][i][macro+j])
#	compositionDelta[k][2][i].remove(compositionDelta[k][2][i][macro+j])
#	compositionEta[k][2][i].remove(compositionEta[k][2][i][macro+j])
#	compositionTheta[k][2][i].remove(compositionTheta[k][2][i][macro+j])		
    for j in range(ap):
      if i != j:
	for k in range(scenario):
	  cpx.variables.delete(compositionDelta[k][2][i][macro+small+j])
#	  cpx.variables.delete(compositionEta[k][2][i][macro+small+j])
	  cpx.variables.delete(compositionTheta[k][2][i][macro+small+j])
	  cpx.variables.delete(compositionNu[k][2][i][macro+small+j])
#	  compositionDelta[k][2][i].remove(compositionDelta[k][2][i][macro+small+j])
#	  compositionEta[k][2][i].remove(compositionEta[k][2][i][macro+small+j])
#	  compositionTheta[k][2][i].remove(compositionTheta[k][2][i][macro+small+j])	
	  
	  
  for i in range(small):
    for j in range(macro):
      if smallCoveredBy[i].count(j) == 0:
	for k in range(scenario):
	  #for l in range(location):
#	  cpx.variables.delete(compositionDelta[k][0][j][macro+i])
#	  cpx.variables.delete(compositionEta[k][0][j][macro+i])
#	  cpx.variables.delete(compositionTheta[k][0][j][macro+i])
	  compositionDelta[k][0][j].remove('dM.'+str(k)+'.'+str(j)+'.'+str(macro+i))
#	  compositionEta[k][0][j].remove('uM.'+str(k)+'.'+str(j)+'.'+str(macro+i))
	  compositionTheta[k][0][j].remove('tM.'+str(k)+'.'+str(j)+'.'+str(macro+i))
	  compositionNu[k][0][j].remove('nM.'+str(k)+'.'+str(j)+'.'+str(macro+i))
  for i in range(ap):
    for j in range(macro):
      if apCoveredBy[i].count(j) == 0:
	for k in range(scenario):
	  #for l in range(location):
#	  cpx.variables.delete(compositionDelta[k][0][j][macro+small+i])
#	  cpx.variables.delete(compositionEta[k][0][j][macro+small+i])
#	  cpx.variables.delete(compositionTheta[k][0][j][macro+small+i])
	  compositionDelta[k][0][j].remove('dM.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))
#	  compositionEta[k][0][j].remove('uM.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))
	  compositionTheta[k][0][j].remove('tM.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))	  
	  compositionNu[k][0][j].remove('nM.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))	
  for i in range(ap):
    for j in range(small):
      if apCoveredBySmall[i].count(j) == 0:
	for k in range(scenario):
	  #for l in range(location):
#	  cpx.variables.delete(compositionDelta[k][1][j][macro+small+i])
#	  cpx.variables.delete(compositionEta[k][1][j][macro+small+i])
#	  cpx.variables.delete(compositionTheta[k][1][j][macro+small+i])
	  compositionDelta[k][1][j].remove('dS.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))
#	  compositionEta[k][1][j].remove('uS.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))
	  compositionTheta[k][1][j].remove('tS.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))	  
	  compositionNu[k][1][j].remove('nS.'+str(k)+'.'+str(j)+'.'+str(macro+small+i))	  
  for i in range(macro):
    for j in range(macro):
      if i != j:
	for k in range(scenario):
#	  cpx.variables.delete(compositionDelta[k][0][i][j])
#	  cpx.variables.delete(compositionEta[k][0][i][j])
#	  cpx.variables.delete(compositionTheta[k][0][i][j])
	  compositionDelta[k][0][i].remove('dM.'+str(k)+'.'+str(i)+'.'+str(j))
#	  compositionEta[k][0][i].remove('uM.'+str(k)+'.'+str(i)+'.'+str(j))
	  compositionTheta[k][0][i].remove('tM.'+str(k)+'.'+str(i)+'.'+str(j))	  
	  compositionNu[k][0][i].remove('nM.'+str(k)+'.'+str(i)+'.'+str(j))	
  for i in range(small):
    for j in range(macro):
      for k in range(scenario):
#	cpx.variables.delete(compositionDelta[k][1][i][j])
#	cpx.variables.delete(compositionEta[k][1][i][j])
#	cpx.variables.delete(compositionTheta[k][1][i][j])
	compositionDelta[k][1][i].remove('dS.'+str(k)+'.'+str(i)+'.'+str(j))
#	compositionEta[k][1][i].remove('uS.'+str(k)+'.'+str(i)+'.'+str(j))
	compositionTheta[k][1][i].remove('tS.'+str(k)+'.'+str(i)+'.'+str(j))	
	compositionNu[k][1][i].remove('nS.'+str(k)+'.'+str(i)+'.'+str(j))	
    for j in range(small):
      if i != j:
	for k in range(scenario):
#	  cpx.variables.delete(compositionDelta[k][1][i][macro+j])
#	  cpx.variables.delete(compositionEta[k][1][i][macro+j])
#	  cpx.variables.delete(compositionTheta[k][1][i][macro+j])
	  compositionDelta[k][1][i].remove('dS.'+str(k)+'.'+str(i)+'.'+str(macro+j))
#	  compositionEta[k][1][i].remove('uS.'+str(k)+'.'+str(i)+'.'+str(macro+j))
	  compositionTheta[k][1][i].remove('tS.'+str(k)+'.'+str(i)+'.'+str(macro+j))	  
	  compositionNu[k][1][i].remove('nS.'+str(k)+'.'+str(i)+'.'+str(macro+j))	
  for i in range(ap):
    for j in range(macro):
      for k in range(scenario):
#	cpx.variables.delete(compositionDelta[k][2][i][j])
#	cpx.variables.delete(compositionEta[k][2][i][j])
#	cpx.variables.delete(compositionTheta[k][2][i][j])
	compositionDelta[k][2][i].remove('dA.'+str(k)+'.'+str(i)+'.'+str(j))
#	compositionEta[k][2][i].remove('uA.'+str(k)+'.'+str(i)+'.'+str(j))
	compositionTheta[k][2][i].remove('tA.'+str(k)+'.'+str(i)+'.'+str(j))	
	compositionNu[k][2][i].remove('nA.'+str(k)+'.'+str(i)+'.'+str(j))
    for j in range(small):
      for k in range(scenario):
#	cpx.variables.delete(compositionDelta[k][2][i][macro+j])
#	cpx.variables.delete(compositionEta[k][2][i][macro+j])
#	cpx.variables.delete(compositionTheta[k][2][i][macro+j])
	compositionDelta[k][2][i].remove('dA.'+str(k)+'.'+str(i)+'.'+str(macro+j))
#	compositionEta[k][2][i].remove('uA.'+str(k)+'.'+str(i)+'.'+str(macro+j))
	compositionTheta[k][2][i].remove('tA.'+str(k)+'.'+str(i)+'.'+str(macro+j))		
	compositionNu[k][2][i].remove('nA.'+str(k)+'.'+str(i)+'.'+str(macro+j))
    for j in range(ap):
      if i != j:
	for k in range(scenario):
#	  cpx.variables.delete(compositionDelta[k][2][i][macro+small+j])
#	  cpx.variables.delete(compositionEta[k][2][i][macro+small+j])
#	  cpx.variables.delete(compositionTheta[k][2][i][macro+small+j])
	  compositionDelta[k][2][i].remove('dA.'+str(k)+'.'+str(i)+'.'+str(macro+small+j))
#	  compositionEta[k][2][i].remove('uA.'+str(k)+'.'+str(i)+'.'+str(macro+small+j))
	  compositionTheta[k][2][i].remove('tA.'+str(k)+'.'+str(i)+'.'+str(macro+small+j))		  
	  compositionNu[k][2][i].remove('nA.'+str(k)+'.'+str(i)+'.'+str(macro+small+j))		  
  return


station_coordinate()
station_covered_in()
station_neighbor()

scenario_prob()
scenarioUserNum(preserved_scenario_number)
print smallInBig
print apInBig
print apInSmall
print neighborBig
print neighborSmall
print preserved_scenario
print preserved_scenario_prob
print preserved_scenario_number
print Ntp
output_coordinate_information(BigCor, 'macrocell Coordinate')
output_coordinate_information(SmallCor, 'small cell Coordinate')
output_coordinate_information(APCor, 'AP Coordinate')
output_userDistr()

get_utility()
powerAct = [[] for i in range(3)]
powerSle = [[] for i in range(3)]
#consumPowDiff = []
for i in range(macro):
  powerAct[0].append(macroActP)
  powerSle[0].append(macroSleP)
for i in range(small):
  powerAct[1].append(smallActP)
  powerSle[1].append(smallSleP)
for i in range(ap):
  powerAct[2].append(apActP)
  powerSle[2].append(apSleP)
addEnergy = [[] for i in range(3)]

for i in range(len(addEnergy)):
  if i == 0:
    for j in range(macro):
      addEnergy[i].append(addMacroEne)
  elif i == 1:
    for j in range(small):
      addEnergy[i].append(addSmallEne)
  else:
    for j in range(ap):
      addEnergy[i].append(addAPEne)  
#scenario_generation()
#print scenario_mean
t1 = time.time()
#create cplex object
cpx = cplex.Cplex()
#ev = cplex.Cplex()
#Parameter example - Limit tree size i memory to 8GB
# Rest of tree is saved on disk
cpx.parameters.mip.limits.treememory.set(8192)
cpx.parameters.mip.strategy.file.set(3)
#objective function
cpx.objective.set_sense(cpx.objective.sense.maximize)
#ev.objective.set_sense(ev.objective.sense.maximize)
#create variables
compositionLambda = [[] for i in range(3)]
#compositionMu = [[] for i in range(3)]
compositionNu = [[[] for j in range(3)] for i in range(scenario)]
compositionAlpha = [[] for i in range(3)]
for i in range(macro):
  compositionAlpha[0].append('aM'+str(i))
for i in range(small):
  compositionAlpha[1].append('aS'+str(i))
for i in range(ap):
  compositionAlpha[2].append('aA'+str(i))
#print compositionAlpha
compositionBeta = [[] for i in range(3)]
for i in range(macro):
  compositionBeta[0].append('bM'+str(i))
for i in range(small):
  compositionBeta[1].append('bS'+str(i))
for i in range(ap):
  compositionBeta[2].append('bA'+str(i))
  
compositionTheta = [[[] for j in range(3)] for i in range(scenario)]
for j in range(scenario):
  #for i in range(macro):
  #listToAdd = [1, 2, 3]
  compositionTheta[j][0] = compositionTheta[j][0] + [[] for i in range(macro)]
  compositionTheta[j][1] = compositionTheta[j][1] + [[] for i in range(small)]
  compositionTheta[j][2] = compositionTheta[j][2] + [[] for i in range(ap)]
  #for k in range(3):

  for l in range(macro):
    for i in range(location):
      compositionTheta[j][0][l].append('tM.'+str(j)+'.'+str(l)+'.'+str(i))
#print compositionTheta[j][0][2]
    #compositionTheta[j][k].append([[] for i in range(small)])
  for l in range(small):
    for i in range(location):
      compositionTheta[j][1][l].append('tS.'+str(j)+'.'+str(l)+'.'+str(i))
    #compositionTheta[j][k].append([[] for i in range(ap)])
  for l in range(ap):
    for i in range(location):
      compositionTheta[j][2][l].append('tA.'+str(j)+'.'+str(l)+'.'+str(i))
      
compositionDelta = [[[] for j in range(3)] for i in range(scenario)]
for j in range(scenario):
  #for i in range(macro):
  #listToAdd = [1, 2, 3]
  compositionDelta[j][0] = compositionDelta[j][0] + [[] for i in range(macro)]
  compositionDelta[j][1] = compositionDelta[j][1] + [[] for i in range(small)]
  compositionDelta[j][2] = compositionDelta[j][2] + [[] for i in range(ap)]
  #for k in range(3):

  for l in range(macro):
    for i in range(location):
      compositionDelta[j][0][l].append('dM.'+str(j)+'.'+str(l)+'.'+str(i))
#print compositionTheta[j][0][2]
    #compositionTheta[j][k].append([[] for i in range(small)])
  for l in range(small):
    for i in range(location):
      compositionDelta[j][1][l].append('dS.'+str(j)+'.'+str(l)+'.'+str(i))
    #compositionTheta[j][k].append([[] for i in range(ap)])
  for l in range(ap):
    for i in range(location):
      compositionDelta[j][2][l].append('dA.'+str(j)+'.'+str(l)+'.'+str(i))
      
#compositionEta = [[[] for j in range(3)] for i in range(scenario)]
#for j in range(scenario):
#  #for i in range(macro):
#  #listToAdd = [1, 2, 3]
#  compositionEta[j][0] = compositionEta[j][0] + [[] for i in range(macro)]
#  compositionEta[j][1] = compositionEta[j][1] + [[] for i in range(small)]
#  compositionEta[j][2] = compositionEta[j][2] + [[] for i in range(ap)]
  #for k in range(3):

#  for l in range(macro):
#    for i in range(location):
#      compositionEta[j][0][l].append('uM.'+str(j)+'.'+str(l)+'.'+str(i))
##print compositionTheta[j][0][2]
#    #compositionTheta[j][k].append([[] for i in range(small)])
#  for l in range(small):
#    for i in range(location):
#      compositionEta[j][1][l].append('uS.'+str(j)+'.'+str(l)+'.'+str(i))
#    #compositionTheta[j][k].append([[] for i in range(ap)])
#  for l in range(ap):
#    for i in range(location):
#      compositionEta[j][2][l].append('uA.'+str(j)+'.'+str(l)+'.'+str(i))
#print compositionTheta
tempList = []
binaryVar()
#print (str(i) for i in compositionAlpha[:])
cpx.variables.add(names = [str(i) for i in (compositionAlpha[0]+compositionAlpha[1]+compositionAlpha[2]) ], types = "C" * (len(compositionAlpha[0])+len(compositionAlpha[1])+len(compositionAlpha[2])))
cpx.variables.add(names = [str(i) for i in (compositionBeta[0]+compositionBeta[1]+compositionBeta[2]) ], types = "C" * (len(compositionBeta[0])+len(compositionBeta[1])+len(compositionBeta[2])))
#ev.variables.add(names = [str(i) for i in (compositionAlpha[0]+compositionAlpha[1]+compositionAlpha[2]) ], types = "C" * (len(compositionAlpha[0])+len(compositionAlpha[1])+len(compositionAlpha[2])))
#ev.variables.add(names = [str(i) for i in (compositionBeta[0]+compositionBeta[1]+compositionBeta[2]) ], types = "C" * (len(compositionBeta[0])+len(compositionBeta[1])+len(compositionBeta[2])))
for i in range(scenario):
  #for j in range(3):
    for k in range(macro):
      #for l in range(location):
	tempList += compositionTheta[i][0][k]
    for k in range(small):
      #for l in range(location):
      tempList += compositionTheta[i][1][k]
    for k in range(ap):
      #for l in range(location):
	tempList += compositionTheta[i][2][k]	
cpx.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))	
#ev.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
del tempList[:]

for i in range(scenario):
  #for j in range(3):
    for k in range(macro):
      #for l in range(location):
	tempList += compositionDelta[i][0][k]
    for k in range(small):
      #for l in range(location):
      tempList += compositionDelta[i][1][k]
    for k in range(ap):
      #for l in range(location):
	tempList += compositionDelta[i][2][k]
cpx.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
#ev.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))	
del tempList[:]

#for i in range(scenario):
#  #for j in range(3):
#    for k in range(macro):
#      #for l in range(location):
#	tempList += compositionEta[i][0][k]
#    for k in range(small):
#      #for l in range(location):
#      tempList += compositionEta[i][1][k]
#    for k in range(ap):
#      #for l in range(location):
#	tempList += compositionEta[i][2][k]
#cpx.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
#ev.variables.add(names = [str(i) for i in tempList ], types = "C" * len(tempList))
#del tempList[:]

cpx.variables.add(names = ['psilon'], types = "C")
temp = 0
consumPowDiff = []
for i in range(len(powerAct)):
  for j in range(len(powerAct[i])):
    consumPowDiff.append(powerAct[i][j] - powerSle[i][j])
    temp += powerSle[i][j]
consumPowDiff.append(temp)
for i in range(len(compositionAlpha)):
  tempList += compositionAlpha[i] 
#tempList.append('dummyVar')
#print 'phase 0'
tempList.append('psilon')

#print 'phase 1'
for i in range(len(compositionDelta)):
  for j in range(len(compositionDelta[i])):
    for k in range(len(compositionDelta[i][j])):
      for l in range(len(compositionDelta[i][j][k])):
	tempList.append(compositionDelta[i][j][k][l])
	consumPowDiff.append(addEnergy[j][k]*prob[i])
	#print 'phase 1'+str(i)+str(j)+str(k)+str(l)
#for i in range(0, len(compositionBeta)-1):
#  for j in range(len(compositionBeta[i])):
#    tempList.append(compositionBeta[i][j])
#    consumPowDiff.append(addEnergy[i][j])

#for i in range(len(addEnergy)):
#  if i == 0:
#    for j in range(len(addEnergy[i])):
#      tempList.append(compositionBeta[i][j])
#      consumPowDiff.append(addEnergy[i][j])
#  elif i == 1:
#    for j in range(len(addEnergy[i])):
#      tempList.append(compositionBeta[i][j])
#      consumPowDiff.append(addEnergy[i][j])
#for i in range(len(compositionTheta)):
#  for j in range(len(compositionTheta[i])):
#    for k in range(len(compositionTheta[i][j])):
#      if j == 0:
#	tempList.append(compositionBeta[j][k])
#	consumPowDiff.append(addEnergy[j][k])
#
#	tempList.append(compositionTheta[i][j][k][k])
#
#	consumPowDiff.append(-1*addEnergy[j][k]*nUser[i][k]*prob[i]/utility[j][k])
#	for l in range(small):
#	  if smallInBig[k].count(l) > 0:
#	    tempList.append(compositionTheta[i][j][k][macro+l])
#	    consumPowDiff.append(-1*addEnergy[j][k]*nUser[i][macro+l]*prob[i]/utility[j][k])
#      elif j == 1:
#	tempList.append(compositionBeta[j][k])
#	consumPowDiff.append(addEnergy[j][k])
#	tempList.append(compositionTheta[i][j][k][k+macro])
#	consumPowDiff.append(-1*addEnergy[j][k]*nUser[i][k+macro]*prob[i]/utility[j][k])
#print 'phase 2' 
print tempList
print consumPowDiff
cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = consumPowDiff)], senses = ["E"], rhs = [1], names = ["power_(1)_"+str(constCounter)])

#cpx.linear_constraints.add(lin_expr = [[['dummyVar'], [1]]], senses = ["E"], rhs = [1], names = ["dummy_(0)_"+str(constCounter)])

temp = 0
del tempList[:]



#print 'phase 3'
#cpx.solve()
#Obtain objective value
#solution = cpx.solution.get_objective_value()
#Obtain values of variables
#variables = cpx.solution.pool.get_values(0)
tempCoef = []
for i in range(scenario):
  for j in range(macro):
    tempList.append(compositionDelta[i][0][j][j])
    tempCoef.append(1)
    for k in range(small):
      if smallInBig[j].count(k) > 0:
	tempList.append(compositionDelta[i][0][j][macro+k])
	tempCoef.append(1)
    for k in range(ap):
      if apInBig[j].count(k) > 0:
	tempList.append(compositionDelta[i][0][j][macro+small+k])
	tempCoef.append(1)
    tempList.append(compositionBeta[0][j])
    tempCoef.append(-1)
    #print tempList
    #print tempCoef
   # if (len(tempList) != len(tempCoef)):
    #  print 'something wrong...'
    constCounter+=1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["E"], rhs = [0], names = ["available(2)_"+str(constCounter)+"#"+str(i)+'.'+str(0)+'.'+str(j)])
    del tempList[:]
    del tempCoef[:]
  for j in range(small):
    tempList.append(compositionDelta[i][1][j][macro+j])
    tempCoef.append(1)
    #for k in range(small):
     # if smallInBig[j].count(k) > 0:
	#tempList.append(compositionTheta[i][0][j][macro+k])
	#tempCoef.append(1)
    for k in range(ap):
      if apInSmall[j].count(k) > 0:
	tempList.append(compositionDelta[i][1][j][macro+small+k])
	tempCoef.append(1)
    tempList.append(compositionBeta[1][j])
    tempCoef.append(-1)
    #print tempList
    #print tempCoef
   # if (len(tempList) != len(tempCoef)):
    #  print 'something wrong...'
    constCounter+=1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["E"], rhs = [0], names = ["available(2)_"+str(constCounter)+"#"+str(i)+'.'+str(1)+'.'+str(j)])
    del tempList[:]
    del tempCoef[:]
  for j in range(ap):
    tempList.append(compositionDelta[i][2][j][macro+small+j])
    tempCoef.append(1)
    #for k in range(small):
     # if smallInBig[j].count(k) > 0:
	#tempList.append(compositionTheta[i][0][j][macro+k])
	#tempCoef.append(1)
    #for k in range(ap):
     # if apInSmall[j].count(k) > 0:
	#tempList.append(compositionTheta[i][1][j][macro+small+k])
	#tempCoef.append(1)
    tempList.append(compositionBeta[2][j])
    tempCoef.append(-1)
    #print tempList
    #print tempCoef
   # if (len(tempList) != len(tempCoef)):
    #  print 'something wrong...'
    constCounter+=1
    cpx.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = tempList, val = tempCoef)], senses = ["E"], rhs = [0], names = ["available(2)_"+str(constCounter)+"#"+str(i)+'.'+str(2)+'.'+str(j)])
    del tempList[:]
    del tempCoef[:]
#print 'constraint 2'
delete(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter)  
#print 'print-out?'
constraint3(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set)
#print 'constrint 3'
constraint4(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set)
#print 'constrint 4'
constraint5(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set)

priorToRemoval = cpx.linear_constraints.get_num()
constraint6(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set)

#remove_duplicate_constraints(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set)

#correctifyConstNum(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval)

constraint7(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval)
#print 'constraint 7'
#constraint8()
constraint9(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval)
#print 'constraint 9'
#constraint10()
constraint11(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval)
objective(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval)
#print 'objective'
#constraint12()
constraint13(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval)
#print 'constraint 13'
#constraint14(cpx, compositionAlpha, compositionBeta, compositionDelta, compositionLambda, compositionNu, compositionTheta, scenario, prob, constCounter, scenario_set, priorToRemoval)
t2 = time.time()
print 'Constructing model took '+str(t2 - t1)+'seconds.'
#find solution

# sys.stdout is the default output stream for log and results
# so these lines may be omitted
cpx.parameters.threads.set(3)
results_write_to = '../setupInfo_/results_'+str(macro)+'_'+str(small)+'_'+str(ap)+'_'+str(max_user)+'_'+str(min_user)+'_o'+str(scenario)+'.log'
cpx.set_results_stream(results_write_to)
cpx.set_log_stream(results_write_to)
cpx.set_warning_stream(results_write_to)
cpx.set_error_stream(results_write_to)
filename_to_write = '../extensiveform/problem_'+str(macro)+'_'+str(small)+'_'+str(ap)+'_'+str(max_user)+'_'+str(min_user)+'_o'+str(scenario)+'.lp'
cpx.write(filename_to_write)
print 'The extnsive form has been written into a file for'+filename_to_write
# Solve
try:
  start_time = cpx.get_time()
  cpx.solve()
  end_time = cpx.get_time()
except CplexSolverError, e:
  print "Exception raised during solve: "
  print e
else:
  sol = cpx.solution
 
  print 
  # solution.get_status() returns an integer code
  print "Solution status = " , sol.get_status(), ":",
  # the following line prints the corresponding string
  print sol.status[sol.get_status()]
  print "utility: " + str(cpx.solution.get_objective_value())
  # Display solution.
  for p in range(macro):
    print "Macrocell " , p, ":" , cpx.solution.get_values(compositionAlpha[0][p]), ",", cpx.solution.get_values(compositionBeta[0][p]), ",", cpx.solution.get_values(compositionLambda[0][p])
  for p in range(small):
    print "Microcell " , p, ":" , cpx.solution.get_values(compositionAlpha[1][p]), ",", cpx.solution.get_values(compositionBeta[1][p]), ",", cpx.solution.get_values(compositionLambda[1][p])
  for p in range(ap):
    print "Access point " , p, ":" , cpx.solution.get_values(compositionAlpha[2][p]), ",", cpx.solution.get_values(compositionBeta[2][p]), ",", cpx.solution.get_values(compositionLambda[2][p])
  for p in range(scenario):
    for i in range(len(compositionDelta[p])):
      for j in range(len(compositionDelta[p][i])):
	for k in range(len(compositionDelta[p][i][j])):
#	if i == 0
	  print compositionDelta[p][i][j][k], ":" , cpx.solution.get_values(compositionDelta[p][i][j][k])
	  print compositionTheta[p][i][j][k], ":" , cpx.solution.get_values(compositionTheta[p][i][j][k])
#	  print compositionEta[p][i][j][k], ":" , cpx.solution.get_values(compositionEta[p][i][j][k])
	  print compositionNu[p][i][j][k], ":" , cpx.solution.get_values(compositionNu[p][i][j][k])
	  print ''
	  #print compositionMu[p][i][j][k], ":" , cpx.solution.get_values(compositionMu[p][i][j][k])
  print "epsilon :", cpx.solution.get_values('psilon')
  print "utility: " + str(cpx.solution.get_objective_value())
  # Open a file
  print 'Start to write the solution into a file.'
  fo = open("../extensiveform/solution.txt", "w")
  fo.write( "The is a solution file.\n\n");
#  temp = 0
#  tempE = 0
#  temp1 = 0
#  tempE1 = 0
#  temp2 = 2
#  for i in range(scenario):
#    for j in range(len(compositionEta[i])):
#      for k in range(len(compositionEta[i][j])):
#	for l in range(len(compositionEta[i][j][k])):
#	  for m in range(location):
#	    if compositionEta[i][j][k][l] == ('uM.'+str(i)+'.'+str(k)+'.'+str(m)) and nUser[i][m] != 0:
#	      temp1 += (cpx.solution.get_values(compositionEta[i][j][k][l])) * (utility[j][k]/nUser[i][m]) * prob[i]
#	      temp += (cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon')) * (cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon')) * (utility[j][k]/nUser[i][m]) * prob[i]
#	      temp2 += (cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon')) * (utility[j][k]/nUser[i][m]) * prob[i]
#	    elif compositionEta[i][j][k][l] == ('uS.'+str(i)+'.'+str(k)+'.'+str(m)) and nUser[i][m] != 0:
#	      temp1 += (cpx.solution.get_values(compositionEta[i][j][k][l])) * (utility[j][k]/nUser[i][m]) * prob[i]
#	      temp += (cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon')) * (cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon')) * (utility[j][k]/nUser[i][m]) * prob[i]
#	      temp2 += (cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon')) * (utility[j][k]/nUser[i][m]) * prob[i]
#	    elif compositionEta[i][j][k][l] == ('uA.'+str(i)+'.'+str(k)+'.'+str(m)) and nUser[i][m] != 0:
#	      temp1 += (cpx.solution.get_values(compositionEta[i][j][k][l])) * (utility[j][k]/nUser[i][m]) * prob[i]
#	      temp += (cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon')) * (cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon')) * (utility[j][k]/nUser[i][m]) * prob[i]
#	      temp2 += (cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon')) * (utility[j][k]/nUser[i][m]) * prob[i]
#	      
#  for h in range(len(compositionAlpha)):
#    for i in range(len(compositionAlpha[h])):
#      if cpx.solution.get_values(compositionAlpha[h][i])/cpx.solution.get_values('psilon') == 1:
#	tempE += powerAct[h][i] * (cpx.solution.get_values(compositionAlpha[h][i])/cpx.solution.get_values('psilon'))
#	tempE1 += powerAct[h][i] * (cpx.solution.get_values(compositionAlpha[h][i]))
#     else:
#	tempE += powerSle[h][i] * (1-(cpx.solution.get_values(compositionAlpha[h][i])/cpx.solution.get_values('psilon')))
#	tempE1 += powerSle[h][i] * (cpx.solution.get_values(compositionAlpha[h][i]))
#  print temp1
#  print tempE1
#  print temp
#  print tempE
#  print temp2

  bigN = macro
  if bigN < small:
    bigN = small
  if bigN < ap:
    bigN = ap
  fo.write( '\t\t\t',)
  for k in range(bigN):
    fo.write( str(k))
    fo.write( '\t')
      
  for i in range(len(compositionAlpha)):
    if i == 0:
      fo.write( '\nMacrocell on/off:\t')
    elif i == 1:
      fo.write( '\nSmall cell on/off:\t')
    elif i == 2:
      fo.write( '\nAccess point on/off:\t')
    for j in range(len(compositionAlpha[i])):
      fo.write( str(cpx.solution.get_values(compositionAlpha[i][j])/cpx.solution.get_values('psilon')))
      fo.write( '\t')
    fo.write( '\n\tbandwidth\t')
    for j in range(len(compositionBeta[i])):
      fo.write( str(cpx.solution.get_values(compositionBeta[i][j])/cpx.solution.get_values('psilon')))
      fo.write( '\t',)
    fo.write('\n\tlambda\t\t')
    for j in range(len(compositionLambda[i])):
      fo.write( str(cpx.solution.get_values(compositionLambda[i][j])))
      fo.write( '\t')
    fo.write('\n')
  fo.write( '\n'  )
  for i in range(scenario):
    fo.write( 'Scenario ')
    fo.write( str(i))
    fo.write( '\t\t')
    for j in range(location):
      fo.write( str(j)+'\t')
      
    for j in range(len(compositionTheta[i])):
      if j == 0:
	
	for k in range(len(compositionTheta[i][j])):
	  fo.write( '\nMacrocell ')
	  fo.write( str(k))
	  fo.write( ' cover:\t')
	  for m in range(location): 
	      for l in range(len(compositionTheta[i][j][k])):
		if compositionTheta[i][j][k][l] == ('tM.'+str(i)+'.'+str(k)+'.'+str(m)):# and (cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon') == 1):
		  fo.write( str(cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon')))
		  #fo.write(compositionTheta[i][j][k][l])
		  fo.write( '\t')
		  break
		elif l == len(compositionTheta[i][j][k]) - 1:
		  fo.write('-')
		  #fo.write(str(m)+', '+str(l))
		  fo.write( '\t')
	  fo.write( '\n')
	  
	#for k in range(len(compositionDelta[i][j])):
	  fo.write( 'Macroce ')
	  fo.write( str(k))
	  fo.write( ' BW:\t\t')
	  for m in range(location): 
	      for l in range(len(compositionDelta[i][j][k])):
		if compositionDelta[i][j][k][l] == ('dM.'+str(i)+'.'+str(k)+'.'+str(m)):
		  #if cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon') > 0:
		
		 
		    fo.write( str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon')))
		    fo.write( '\t')
		    break
		  #else:
		elif l == len(compositionDelta[i][j][k]) - 1:
		  fo.write('-')
		  fo.write( '\t')
	  fo.write( '\n')		
	  
	#for k in range(len(compositionEta[i][j])):
#	  fo.write( 'Macrocell ')
#	  fo.write( str(k))
#	  fo.write( ' Eta:\t')
#	  for m in range(location): 
#	      for l in range(len(compositionEta[i][j][k])):
#		if compositionEta[i][j][k][l] == ('uM.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon') > 0:
#		
#		 
#		  fo.write( str(cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon')))
#		  fo.write( '\t')
#		  break
#		elif l == len(compositionEta[i][j][k]) - 1:
#		  fo.write('-')
#		  fo.write( '\t')
#	  fo.write( '\n')
	  
	#for k in range(len(compositionNu[i][j])):
	  fo.write( 'Macrocel ')
	  fo.write( str(k))
	  fo.write( ' Nu:\t\t')
	  for m in range(location): 
	      for l in range(len(compositionNu[i][j][k])):
		if compositionNu[i][j][k][l] == ('nM.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionNu[i][j][k][l]) > 0:
		
		 
		  fo.write( str(cpx.solution.get_values(compositionNu[i][j][k][l])))
		  fo.write( '\t')
		  break
		elif l == len(compositionNu[i][j][k]) - 1:
		  fo.write('-')
		  fo.write( '\t')
	  fo.write( '\n')	 
	fo.write( '\n')
      elif j == 1:
	for k in range(len(compositionTheta[i][j])):
	  fo.write( '\nSmall cell ')
	  fo.write( str(k))
	  fo.write( ' cover:\t')
	  for m in range(location): 
	      for l in range(len(compositionTheta[i][j][k])):
		if compositionTheta[i][j][k][l] == ('tS.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon') == 1:
		
		 
		  fo.write( str(cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon')))
		  fo.write( '\t')
		  break
		elif l == len(compositionTheta[i][j][k]) - 1:
		  fo.write('-')
		  fo.write( '\t')
	  fo.write( '\n')
	  
	#for k in range(len(compositionDelta[i][j])):
	  fo.write( 'Small cell ')
	  fo.write(str( k))
	  fo.write( ' BW:\t')
	  for m in range(location): 
	      for l in range(len(compositionDelta[i][j][k])):
		if compositionDelta[i][j][k][l] == ('dS.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon') > 0:
		
		 
		  fo.write( str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon')))
		  fo.write( '\t')
		  break
		elif l == len(compositionDelta[i][j][k]) - 1:
		  fo.write('-')
		  fo.write( '\t')
	  fo.write( '\n')		
	  
	#for k in range(len(compositionEta[i][j])):
#	  fo.write( 'Small cell ')
#	  fo.write( str(k))
#	  fo.write( ' Eta:\t')
#	  for m in range(location): 
#	      for l in range(len(compositionEta[i][j][k])):
#		if compositionEta[i][j][k][l] == ('uS.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon') > 0:
#		
#		 
#		  fo.write( str(cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon')))
#		  fo.write( '\t')
#		  break
#		elif l == len(compositionEta[i][j][k]) - 1:
#		  fo.write('-')
#		  fo.write( '\t')
#	  fo.write( '\n')
	  
	#for k in range(len(compositionNu[i][j])):
	  fo.write( 'Small cell ')
	  fo.write( str(k))
	  fo.write( ' Nu:\t')
	  for m in range(location): 
	      for l in range(len(compositionNu[i][j][k])):
		if compositionNu[i][j][k][l] == ('nS.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionNu[i][j][k][l]) > 0:
		
		 
		  fo.write( str(cpx.solution.get_values(compositionNu[i][j][k][l])) )
		  fo.write( '\t')
		  break
		elif l == len(compositionNu[i][j][k]) - 1:
		  fo.write('-')
		  fo.write( '\t')
	  fo.write( '\n')	 
	fo.write( '\n')	
      elif j == 2:
	for k in range(len(compositionTheta[i][j])):
	  fo.write( '\nAccess Point ')
	  fo.write( str(k))
	  fo.write( ' cover:\t')
	  for m in range(location): 
	      for l in range(len(compositionTheta[i][j][k])):
		if compositionTheta[i][j][k][l] == ('tA.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon') == 1:
		
		 
		  fo.write( str(cpx.solution.get_values(compositionTheta[i][j][k][l])/cpx.solution.get_values('psilon')))
		  fo.write( '\t')
		  break
		elif l == len(compositionTheta[i][j][k]) - 1:
		  fo.write('-')
		  fo.write( '\t')
	  fo.write( '\n')
	  
	#for k in range(len(compositionDelta[i][j])):
	  fo.write( 'Access Point ')
	  fo.write( str(k))
	  fo.write( ' BW:\t')
	  for m in range(location): 
	      for l in range(len(compositionDelta[i][j][k])):
		if compositionDelta[i][j][k][l] == ('dA.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon') > 0:
		
		 
		  fo.write( str(cpx.solution.get_values(compositionDelta[i][j][k][l])/cpx.solution.get_values('psilon')))
		  fo.write( '\t')
		  break
		elif l == len(compositionDelta[i][j][k]) - 1:
		  fo.write('-')
		  fo.write( '\t')
	  fo.write( '\n')		
	  
	#for k in range(len(compositionEta[i][j])):
#	  fo.write( 'Access Point ')
#	  fo.write( str(k))
#	  fo.write( ' Eta:\t')
#	  for m in range(location): 
#	      for l in range(len(compositionEta[i][j][k])):
#		if compositionEta[i][j][k][l] == ('uA.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon') > 0:
#		
#		 
#		  fo.write( str(cpx.solution.get_values(compositionEta[i][j][k][l])/cpx.solution.get_values('psilon')))
#		  fo.write( '\t')
#		  break
#		elif l == len(compositionEta[i][j][k]) - 1:
#		  fo.write('-')
#		  fo.write( '\t')
#	  fo.write( '\n')
	  
	#for k in range(len(compositionNu[i][j])):
	  fo.write( 'Access Point ')
	  fo.write( str(k))
	  fo.write( ' Nu:\t')
	  for m in range(location): 
	      for l in range(len(compositionNu[i][j][k])):
		if compositionNu[i][j][k][l] == ('nA.'+str(i)+'.'+str(k)+'.'+str(m)):# and cpx.solution.get_values(compositionNu[i][j][k][l]) > 0:
		
		 
		  fo.write( str(cpx.solution.get_values(compositionNu[i][j][k][l])))
		  fo.write( '\t')
		  break
		elif l == len(compositionNu[i][j][k]) - 1:
		  fo.write( '-')
		  fo.write( '\t')
	  fo.write( '\n')	 
      fo.write( '\n')
      fo.write( '==================================================\n')
      
	
  # Close opened file
  fo.close()
  
  filename_to_write = '../extensiveform/obj.txt'
  fo = open(filename_to_write, 'a')
  fo.write('================================A new run starts==========================================\n')
  fo.write(str(macro)+'_'+str(small)+'_'+str(ap)+'_'+str(max_user)+'_'+str(min_user)+'_'+str(scenario)+'\t'+str(t2-t1)+'\t'+str(cpx.solution.get_objective_value())+'\t'+str(end_time-start_time)+'\n')
  print 'Finish recording the objective value of the original problem...'
  fo.close()
  
  band_allocation()
  
  print 'Begin to work on the scenario-reduced problems....'
  
#p = cplex.Cplex()
  for i in range(len(preserved_scenario_number)):
    print 'problem '+str(i)
    preserved_scenario_model(preserved_scenario_number[i], preserved_scenario[i], preserved_scenario_prob[i], i)
    print 'completed'
  print 'All problems have been sovled.'
  
  filename_to_write = '../extensiveform/obj.txt'
  fo = open(filename_to_write, 'a')
  fo.write('================================A new run ends==========================================\n')
  fo.close()

  

  