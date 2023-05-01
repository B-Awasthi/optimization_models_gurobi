from random import randint, uniform
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/staffing.py
# Below implementation is in Gurobi
# =============================================================================


# function to generate data
def gen_data(m, n, n0):
    # m is number of time intervals, n is number of shifts
    R = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    for i in range(m):  # Staffing needs
        R[i][-1] = randint(10, 20)
    n1 = n - n0  # Part-time
    d0 = int(round(m / n0) + 1)  # Full-time shift
    d1 = int(round(d0 / 2))  # Part-time shift
    for j in range(n0):  # Pay for full-time-shift
        R[-1][j] = round(uniform(15, 20) * d0, 2)
    for j in range(n0, n):
        R[-1][j] = round(uniform(10, 15) * d1, 2)
    s = 0
    for j in range(n0):  # Full-time shift layout
        for i in range(s, s + d0):
            R[i % m][j] = 1
        s = s + d0 - 1
    s = [R[i][-1] for i in range(m)].index(max(R[i][-1] for i in range(m)))
    for j in range(n0, n):  # Part-time shift layout
        for i in range(s, s + d1):
            R[i % m][j] = 1
        s = s + d1 + 1
    return R


M = gen_data(10, 8, 4)
nf = 4

"""
M = gen_data(m, n, n0)
m : number of time intervals
n : number of shifts
n0 : number of full time employees

M : last column is number of required persons for each time interval
  : last row is cost of putting a person in a particular shift
"""


def solve_model(M, nf, Q=None, P=None, no_part=False):
    model = gp.Model("Staffing")

    nbt, n = len(M) - 1, len(M[0]) - 1
    B = sum(M[t][-1] for t in range(len(M) - 1))

    x = model.addVars(range(n), lb=0, ub=B, vtype=GRB.INTEGER)

    model.addConstrs(
        gp.quicksum(M[t][i] * x[i] for i in range(n)) >= M[t][-1] for t in range(nbt)
    )

    if Q:
        model.addConstrs(x[i] >= Q[i] for i in range(n))

    if P:
        model.addConstr(gp.quicksum(x[i] for i in range(nf)) >= P)

    if no_part:
        for t in range(nbt):
            model.addConstr(
                B * gp.quicksum([M[t][i] * x[i] for i in range(nf)])
                >= gp.quicksum([M[t][i] * x[i] for i in range(nf, n)])
            )

    model.setObjective(x.prod(M[-1][:-1]), sense=GRB.MINIMIZE)
    model.optimize()

    sol = {k: abs(v.X) for k, v in x.items()}

    return model.status, model.ObjVal, sol


if __name__ == "__main__":
    optimality_status, objval, sol = solve_model(M, nf)
