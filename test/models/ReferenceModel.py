# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 09:33:28 2013

@author: Dinakar Gade, Sarah M.Ryan
Created for Class IE633x - Stochastic Programming, Spring 2013

This model encodes the Stochastic Facility Location Problem with
variable distribution pattern and  uncertain demand from Chapter 2 of
Birge J. and Louveaux, F., (2011) "Introduction to Stochastic Programming"
"""
print "Hello"
#import coopr pyomo
from coopr.pyomo import *

#Our model will be an abstract model - Separates model from data
model = AbstractModel()

#Potential facility location, index, j = 1,..,n
model.Plants    = Set()

#Clients, j = 1,..,m
model.Clients   = Set()

# Demand of client i
model.Demand    = Param(model.Clients, within = NonNegativeReals, default = 0.0) #d_i in book

#Fixed cost of Plant j
model.FixedCost = Param(model.Plants, within = NonNegativeReals, default = 0.0) #c_j in book

#Capacity Cost of plant j
model.CapacityCost = Param(model.Plants, within = NonNegativeReals, default = 0.0) #g_j in book

#Unit price for client i
model.UnitPrice = Param(model.Clients, within = Reals, default = 0.0) #r_i in book

#Variable operating cost of plant j
model.VariableCost = Param(model.Plants, within = NonNegativeReals, default = 0.0) #v_j in book

#Transportation cost from plant j to client i
model.TransportationCost = Param(model.Clients, model.Plants, within = NonNegativeReals, default = 0.0) # t_ij in book

# A function to compute a calculated parameter
#Function to calculate revenue from the input cost/price/transportation cost data
def calculate_revenue_rule(m,i,j):
    return (m.UnitPrice[i] - m.VariableCost[j] - m.TransportationCost[i,j])*m.Demand[i]

model.Revenue = Param(model.Clients, model.Plants, within=Reals, initialize=calculate_revenue_rule) #q_ij in book


#Decision Variables

model.PlantOpen = Var(model.Plants, within = Binary) # Decide whether or not to open a plant x_j in book
model.PlantCapacity = Var(model.Plants, within = NonNegativeReals) # w_j in book
model.FractionDemandServed = Var(model.Clients, model.Plants, within = NonNegativeReals) #y_ij in book

model.FirstStageCost = Var(within = Reals) #Auxiliary variable: Need to model first-stage cost for PySP specifiation
model.SecondStageCost = Var(within = Reals) #Auxiliary variable: Need to model second-stage cost for PySP specification

#Constrains:

def demand_constraint_rule(m,i):
    constraint_expr = 0
    for j in m.Plants:
        constraint_expr +=  m.FractionDemandServed[i,j]
    
    return constraint_expr <= 1.0

model.DemandConstraint = Constraint(model.Clients, rule = demand_constraint_rule)

def shipping_rule(m,i,j):
    return m.FractionDemandServed[i,j] <= m.PlantOpen[j]

model.ShippingConstraint = Constraint(model.Clients, model.Plants, rule = shipping_rule)

def capacity_rule(m,j):
    constraint_expr = 0
    for i in m.Clients:
        constraint_expr += m.Demand[i]*m.FractionDemandServed[i,j]
    
    return constraint_expr <= m.PlantCapacity[j]
model.CapacityConstraint = Constraint(model.Plants, rule = capacity_rule)


def first_stage_cost_rule(m):
    obj_expr = 0
    for j in m.Plants:
        obj_expr -= (m.FixedCost[j]*m.PlantOpen[j] + m.CapacityCost[j]*m.PlantCapacity[j])
    
    return m.FirstStageCost == obj_expr
model.ComputeFirstStageCost = Constraint(rule = first_stage_cost_rule)

def second_stage_cost_rule(m):
    obj_expr = 0
    for i in m.Clients:
        for j in m.Plants:
            obj_expr += m.Revenue[i,j]*m.FractionDemandServed[i,j]
    
    return m.SecondStageCost == obj_expr

model.ComputeSecondStageCost = Constraint(rule = second_stage_cost_rule)
    


#objective
def obj_rule(m):
    return m.FirstStageCost + m.SecondStageCost
 
model.MaxProfit = Objective(rule = obj_rule, sense = maximize)


