# -*- coding: utf-8 -*-

#import coopr pyomo
from coopr.pyomo import *

#Our model will be an abstract model - Separates model from data
model = AbstractModel()


model.Shifts    = Set()


model.Overtime   = Set()
model.Scenarios = Set()


model.DailyCost    = Param(model.Shifts, within = NonNegativeReals, default = 0.0) 

  
model.OTCost = Param(model.Scenarios, model.Overtime, within = NonNegativeReals, default = 5.556)
model.CoverPatient = Param(model.Shifts, within = NonNegativeReals, default = 0.0)
model.Demand = Param(model.Scenarios, model.Overtime, within = NonNegativeReals, default = 0.0)

#Decision Variables

model.ShiftDay = Var(model.Shifts, within = NonNegativeIntegers) 

model.OTScenario = Var(model.Scenarios, model.Overtime, within = NonNegativeIntegers) 
model.FirstStageCost = Var(within = Reals) #Auxiliary variable: Need to model first-stage cost for PySP specifiation
model.SecondStageCost = Var(within = Reals) #Auxiliary variable: Need to model second-stage cost for PySP specification


#Constrains:

def demand_constraint_rule1(m,i):
    constraint_expr = 0
    constraint_expr += (m.CoverPatient['Sat']*m.ShiftDay['Sat'] + m.CoverPatient['SatSun']*m.ShiftDay['SatSun'] + m.CoverPatient['SatMon']*m.ShiftDay['SatMon'] + m.OTScenario[i,'SatOT'])
    return constraint_expr >= m.Demand[i,'SatOT']
    
model.DemandConstraint1 = Constraint(model.Scenarios, rule = demand_constraint_rule1)

def demand_constraint_rule2(m,i):
    constraint_expr = 0
    constraint_expr += (m.CoverPatient['Sun']*m.ShiftDay['Sun'] + m.CoverPatient['SatSun']*m.ShiftDay['SatSun'] + m.CoverPatient['SunMon']*m.ShiftDay['SunMon'] + m.OTScenario[i,'SunOT'])
    return constraint_expr >= m.Demand[i,'SunOT']
    
model.DemandConstraint2 = Constraint(model.Scenarios,rule = demand_constraint_rule2)
   
def demand_constraint_rule3(m,i):
    constraint_expr = 0   
    constraint_expr += (m.CoverPatient['Mon']*m.ShiftDay['Mon'] + m.CoverPatient['SatMon']*m.ShiftDay['SatMon'] + m.CoverPatient['SunMon']*m.ShiftDay['SunMon'] + m.OTScenario[i,'MonOT'])
    return constraint_expr >= m.Demand[i,'MonOT']
    
model.DemandConstraint3 = Constraint(model.Scenarios, rule = demand_constraint_rule3)


def total_nurse(m):
    constraint_expr = 0
    for i in m.Shifts:
        constraint_expr += m.ShiftDay[i]
    
    return constraint_expr <= 15.0 
model.NurseConstraint = Constraint(rule = total_nurse)


def first_stage_cost_rule(m):
    obj_expr = 0
    for j in m.Shifts:
        obj_expr += m.DailyCost[j]*m.ShiftDay[j]
    
    return m.FirstStageCost == obj_expr
model.ComputeFirstStageCost = Constraint(rule = first_stage_cost_rule)

def second_stage_cost_rule(m):
    obj_expr = 0
    for i in m.Scenarios:
        for j in m.Overtime:
            obj_expr += m.OTCost[i,j]*m.OTScenario[i,j]
    
    return m.SecondStageCost == obj_expr

model.ComputeSecondStageCost = Constraint(rule = second_stage_cost_rule)
    


#objective
def obj_rule(m):
    return m.FirstStageCost + m.SecondStageCost
 
model.MinCost = Objective(rule = obj_rule, sense = minimize)


 
