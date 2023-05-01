from random import randint
import itertools
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/facility_location.py
# Below implementation is in Gurobi
# =============================================================================


def gen_dcost(m, n):
    R = []
    S = 0
    for i in range(m):
        RR = []
        for j in range(n):
            RR.append(randint(10, 30))
        RR.append(randint(500, 700))
        R.append(RR)
        S += RR[-1]
    A = S / n
    RR = []
    for i in range(n):
        RR.append(randint(int(0.5 * A), int(0.75 * A)))
    RR.append(0)
    R.append(RR)
    return R


def gen_fcost(m):
    return [randint(4200, 6500) for i in range(m)]


D = gen_dcost(4, 6)
"""
gen_dcost(m, n)

m : number of plants
n : number of cities

D : each row corresponds to a supplier
    D[0] each entry represents the variable cost from plant i to city j.
    last entry is the total units that plant 0 can supply
    
    last row represensts the demand for each city to be met
"""


F = gen_fcost(4)


def solve_model(D, F):
    model = gp.Model("Facility location problem")
    m, n = len(D) - 1, len(D[0]) - 1
    B = sum(D[-1][j] * max(D[i][j] for i in range(m)) for j in range(n))
    indx = list(itertools.product(range(m), range(n)))
    upper_bound = [D[i][-1] for i in [j[0] for j in indx]]
    x = model.addVars(indx, lb=0, ub=upper_bound, vtype=GRB.CONTINUOUS)

    y = model.addVars(range(m), vtype=GRB.BINARY)

    Fcost = model.addVar(lb=0, ub=B, vtype=GRB.CONTINUOUS)
    Dcost = model.addVar(lb=0, ub=B, vtype=GRB.CONTINUOUS)

    model.addConstrs(x.sum(i, "*") <= D[i][-1] * y[i] for i in range(m))

    model.addConstrs(x.sum("*", j) == D[-1][j] for j in range(n))

    model.addConstr(Fcost == y.prod(F))

    model.addConstr(
        Dcost == gp.quicksum(x[i, j] * D[i][j] for i in range(m) for j in range(n))
    )

    model.setObjective(Dcost + Fcost, sense=GRB.MINIMIZE)
    model.optimize()

    x_sol = {k: v for k, v in x.items() if v.X > 0}
    y_sol = [i for i in y if y[i].X > 0]

    return model.ObjVal, x_sol, y_sol, Fcost.X, Dcost.X


if __name__ == "__main__":
    objval, x_sol, y_sol, Fcost, Dcost = solve_model(D, F)
