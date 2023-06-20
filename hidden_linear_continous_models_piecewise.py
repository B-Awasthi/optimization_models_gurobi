import gurobipy as gp
from gurobipy import GRB


model = gp.Model()

units = model.addVar(lb=0, ub=1000, name="units")
model.setAttr("LB", units, 250)
model.setAttr("UB", units, 250)

cost = model.addVar(lb=0, ub=GRB.INFINITY, name="cost")

model.addGenConstrPWL(
    units,
    cost,
    [0, 148, 310, 501, 617, 762, 959],
    [0, 3552, 8088, 14200, 18144, 23364, 31244],
)

model.setObjective(cost, sense=GRB.MINIMIZE)
model.optimize()


# Alternate : use piecewise linear objective

# model = gp.Model()

# cost = model.addVar(lb=0, ub=GRB.INFINITY, name="cost")
# model.setAttr("LB", cost, 250)
# model.setAttr("UB", cost, 250)

# model.setPWLObj(
#     cost,
#     [0, 148, 310, 501, 617, 762, 959],
#     [0, 3552, 8088, 14200, 18144, 23364, 31244],
# )

# model.optimize()
