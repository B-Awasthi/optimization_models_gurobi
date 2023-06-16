from random import randint
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/features.py
# Below implementation is in Gurobi
# =============================================================================


def inner(a, b):
    s = 0
    for i in range(len(a)):
        s += a[i] * b[i]
    return s


def gen_features(n, m):
    # Generating n vectors of m features linearly separable
    a = gen_hyperplane(m)
    A, B, i = [], [], 0
    while len(A) < n:
        x = [randint(-10, 10) for _ in range(m)]
        if inner(a[0:m], x) < a[m] - 1:
            A.append(x)
    while len(B) < n:
        x = [randint(-10, 10) for _ in range(m)]
        if inner(a[0:m], x) > a[m] + 1:
            B.append(x)
    return A, B, a


def gen_hyperplane(m):
    return [randint(-10, 10) for _ in range(m + 1)]


A, B, a = gen_features(5, 3)

n, ma, mb = len(A[0]), len(A), len(B)
model = gp.Model("classification")

ya = model.addVars(range(ma), lb=0, ub=99)

yb = model.addVars(range(mb), lb=0, ub=99)

a = model.addVars(range(n + 1), lb=-99, ub=99)
model.addConstrs(
    ya[i] >= a[n] + 1 - gp.quicksum(a[j] * A[i][j] for j in range(n)) for i in range(ma)
)

model.addConstrs(
    yb[i] >= gp.quicksum(a[j] * B[i][j] for j in range(n)) - a[n] + 1 for i in range(mb)
)

Agap = gp.quicksum(ya)

Bgap = gp.quicksum(yb)

model.setObjective(Agap + Bgap, sense=GRB.MINIMIZE)

model.optimize()
