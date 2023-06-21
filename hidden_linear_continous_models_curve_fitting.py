import gurobipy as gp
from gurobipy import GRB

t_i = [0.1584, 0.8454, 2.1017, 3.1966, 4.056, 4.9931, 5.8574, 7.1474, 8.1859, 9.0349]
f_i = [
    0.0946,
    0.2689,
    5.8285,
    14.8898,
    25.6134,
    38.3952,
    43.5065,
    91.3715,
    119.075,
    115.7737,
]

D = list(zip(t_i, f_i))


def solve_model(D, deg=1, objective=0):
    n = len(D)
    model = gp.Model()

    a = model.addVars(range(1 + deg), lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS)

    u = model.addVars(range(n), vtype=GRB.CONTINUOUS)

    v = model.addVars(range(n), vtype=GRB.CONTINUOUS)

    e = model.addVar(vtype=GRB.CONTINUOUS)

    for i in range(n):
        model.addConstr(
            D[i][1] == u[i] - v[i] + sum(a[j] * D[i][0] ** j for j in range(1 + deg))
        )

    for i in range(n):
        model.addConstr(u[i] <= e)
        model.addConstr(v[i] <= e)

    if objective:
        cost = e
    else:
        cost = gp.quicksum(u[i] + v[i] for i in range(n))

    model.setObjective(cost, sense=GRB.MINIMIZE)

    model.optimize()

    return model.ObjVal, [a[i].X for i in range(1 + deg)]


obj_val, a = solve_model(D, deg=1, objective=0)
