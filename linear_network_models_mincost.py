from random import randint
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/mincost.py
# Below implementation is in Gurobi
# =============================================================================


# function to generate data
def gen_data(m, n):
    R = []
    S = 0
    for i in range(m):
        RR = []
        for j in range(n):
            yesno = 1 - randint(0, 1) * randint(0, 1)
            RR.append(randint(10, 30) * yesno)
        RR.append(randint(500, 700))
        R.append(RR)
        S += RR[-1]
    A = S / n
    RR = []
    for i in range(n):
        RR.append(randint(int(0.75 * A), int(1.1 * A)))
    RR.append(0)
    R.append(RR)
    return R


D = gen_data(4, 5)

"""
gen_data(m, n)

m : number of plants
n : number of cities
D : is a 2 dimensional array indexed by m, n
D : last row of D represents the demand to be met for each cities
D : last column represents the supply limit of each of the plants
"""


def solve_model(D):
    model = gp.Model("Mincost flow problem")
    m, n = len(D) - 1, len(D[0]) - 1
    B = sum([D[-1][j] for j in range(n)])
    nodes_list = [(i, j) for j in range(n) for i in range(m) if D[i][j] > 0]

    x = model.addVars(nodes_list, vtype=GRB.CONTINUOUS, lb=0, ub=B)

    model.addConstrs(D[i][-1] >= x.sum(i, "*") for i in range(m))

    model.addConstrs(D[-1][j] <= x.sum("*", j) for j in range(n))

    cost = gp.quicksum(x[i, j] * D[i][j] for i, j in nodes_list)

    model.setObjective(cost, sense=GRB.MINIMIZE)
    model.optimize()

    solution = {i: x[i].X for i in x}

    return model.ObjVal, solution


if __name__ == "__main__":
    solve_model(D)
