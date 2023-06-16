from random import randint
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/project_management.py
# Below implementation is in Gurobi
# =============================================================================


def gen_data(n):
    R = []
    S = 0
    for i in range(n):
        RR = [i]  # Task number
        RR.append(randint(2, 8))  # Duration
        P = []
        for j in range(i):
            if randint(0, 1) * randint(0, 1):
                P.append(j)
        RR.append(P)
        R.append(RR)
    return R


D = gen_data(5)

model = gp.Model("project_management")

n = len(D)
_max = sum(D[i][1] for i in range(n))

t = model.addVars(n, lb=0, ub=_max)
total = model.addVar(lb=0, ub=_max)

for i in range(n):
    model.addConstr(t[i] + D[i][1] <= total)

    for j in D[i][2]:
        model.addConstr(t[j] + D[j][1] <= t[i])

model.setObjective(total, sense=GRB.MINIMIZE)

model.optimize()

# display solution
for i in t:
    print(str(i) + " --> " + str(t[i].X))
