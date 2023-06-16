from random import randint
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/gas_blend.py
# Below implementation is in Gurobi
# =============================================================================


def gen_raw(n):
    R = []
    for i in range(n):
        R.append([randint(80, 99), randint(600, 1000), 0])
    avgr = sum([R[i][0] for i in range(n)]) / float(n)
    for i in range(n):
        p = randint(50, 55) + 4 * R[i][0] / avgr
        R[i][2] = round(p, 2)
    return R


def gen_refined(n):
    R = []
    for i in range(n):
        R.append([randint(82, 96), randint(100, 500), randint(600, 20000), 0])
    avgr = sum([R[i][0] for i in range(n)]) / float(n)
    for i in range(n):
        p = 61.0 + R[i][0] / avgr
        R[i][3] = round(p, 2)
    return R


C = gen_raw(5)
D = gen_refined(5)

model = gp.Model("gas_blend")

nR, nF = len(C), len(D)
Roc, Rmax, Rcost = 0, 1, 2
Foc, Fmin, Fmax, Fprice = 0, 1, 2, 3

G = model.addVars([(i, j) for i in range(nR) for j in range(nF)], lb=0, ub=10000)

_max_G = [C[i][Rmax] for i in range(nR)]
R = model.addVars(range(nR), lb=0, ub=_max_G)

_min_F = [D[j][Fmin] for j in range(nF)]
_max_F = [D[j][Fmax] for j in range(nF)]
F = model.addVars(range(nF), lb=_min_F, ub=_max_F)

for i in range(nR):
    model.addConstr(R[i] == gp.quicksum(G[i, j] for j in range(nF)))
for j in range(nF):
    model.addConstr(F[j] == gp.quicksum(G[i, j] for i in range(nR)))
for j in range(nF):
    model.addConstr(
        F[j] * D[j][Foc] == gp.quicksum(G[i, j] * C[i][Roc] for i in range(nR))
    )


cost = gp.quicksum(R[i] * C[i][Rcost] for i in range(nR))
price = gp.quicksum(F[j] * D[j][Fprice] for j in range(nF))

model.setObjective(price - cost, sense=GRB.MAXIMIZE)

model.optimize()
