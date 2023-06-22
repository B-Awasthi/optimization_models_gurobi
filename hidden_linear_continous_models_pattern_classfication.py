from random import randint
import gurobipy as gp
from gurobipy import GRB


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


A, B, _ = gen_features(5, 5)


def solve_margins_classification(A, B):
    n, ma, mb = len(A[0]), len(A), len(B)
    model = gp.Model()

    ua = model.addVars(range(ma), lb=0, ub=99, vtype=GRB.CONTINUOUS)

    la = model.addVars(range(ma), lb=0, ub=99, vtype=GRB.CONTINUOUS)

    ub = model.addVars(range(mb), lb=0, ub=99, vtype=GRB.CONTINUOUS)

    lb = model.addVars(range(mb), lb=0, ub=99, vtype=GRB.CONTINUOUS)

    a = model.addVars(range(n + 1), lb=-99, ub=99, vtype=GRB.CONTINUOUS)

    e = model.addVar(lb=-99, ub=99, vtype=GRB.CONTINUOUS)

    for i in range(ma):
        model.addConstr(0 >= a[n] + 1 - gp.quicksum(a[j] * A[i][j] for j in range(n)))
        model.addConstr(
            a[n] == gp.quicksum(a[j] * A[i][j] - ua[i] + la[i] for j in range(n))
        )
        model.addConstr(e <= ua[i])
        model.addConstr(e <= la[i])
    for i in range(mb):
        model.addConstr(0 >= gp.quicksum(a[j] * B[i][j] for j in range(n)) - a[n] + 1)
        model.addConstr(
            a[n] == gp.quicksum(a[j] * B[i][j] - ub[i] + lb[i] for j in range(n))
        )

        model.addConstr(e <= ub[i])

        model.addConstr(e <= lb[i])

    model.setObjective(e, sense=GRB.MAXIMIZE)
    model.optimize()

    return model.ObjVal, [a[i].X for i in a]


obj_val, a = solve_margins_classification(A, B)
