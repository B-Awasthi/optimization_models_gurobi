from random import randint
from math import sqrt
import gurobipy as gp
from gurobipy import GRB


def dist(p1, p2):
    return int(round(sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)) / 10)


def gen_data(n):
    points = [(randint(1, 1000), randint(1, 1000)) for i in range(n)]
    points.sort()
    R = []
    S = 0
    for i in range(n):
        RR = []
        for j in range(n):
            if i == j or abs(i - j) > 0.5 * n:
                d = 0
            else:
                perturb = randint(0, 1)
                d = 0 if perturb == 0 else dist(points[i], points[j]) * perturb
            RR.append(d)
        R.append(RR)
    return R


D = gen_data(15)


def solve_model(D, Start=None, End=None):
    model, n = gp.Model("Shortest path problem"), len(D)
    if Start is None:
        Start, End = 0, len(D) - 1

    nodes_list = [(i, j) for j in range(n) for i in range(n) if D[i][j] > 0]
    x = model.addVars(nodes_list, vtype=GRB.BINARY)

    for i in range(n):
        if i == Start:
            model.addConstr(x.sum("*", Start) <= 0)
            model.addConstr(x.sum(Start, "*") == 1)
        elif i == End:
            model.addConstr(x.sum("*", End) == 1)
            model.addConstr(x.sum(End, "*") <= 0)
        else:
            model.addConstr(x.sum(i, "*") == x.sum("*", i))

    obj = gp.quicksum(x[i, j] * D[i][j] for i, j in nodes_list)
    model.setObjective(obj, sense=GRB.MINIMIZE)
    model.optimize()

    Path, Cost, Cumul, node = [Start], [0], [0], Start
    while model.Status == 2 and node != End and len(Path) < n:
        next = [i for i in [j for i, j in nodes_list if i == node] if x[node, i].X == 1][
            0
        ]
        Path.append(next)
        Cost.append(D[node][next])
        Cumul.append(Cumul[-1] + Cost[-1])
        node = next
    return model.ObjVal, Path, Cost, Cumul


if __name__ == "__main__":
    solve_model(D, Start=0, End=13)
