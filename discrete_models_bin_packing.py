from random import randint
from math import ceil
import itertools
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/bin_packing.py
# Below implementation is in Gurobi
# =============================================================================


def gen_data(n):
    R, T = [], 0
    for i in range(n):
        RR = [randint(6, 10), randint(200, 500)]
        T += RR[0] * RR[1]
        R.append(RR)
    return R, randint(1200, 1500)


def bound_trucks(w, W):
    nb, tot = 1, 0
    for i in range(len(w)):
        if tot + w[i] < W:
            tot += w[i]
        else:
            tot = w[i]
            nb = nb + 1
    return nb, ceil(sum(w) / W)


D = gen_data(5)

"""
gen_data(n)

n : number of weight classes
D : D[1] is weight of each truck
    D[0] is a list with 2 entities - first is number of parcels and
                                     second is the weight of each parcel
"""


def solve_model(D, W=D[1], symmetry_break=False, knapsack=True):
    model = gp.Model("Bin Packing")
    nbC, nbP = len(D[0]), sum([P[0] for P in D[0]])
    w = [e for sub in [[d[1]] * d[0] for d in D[0]] for e in sub]

    nbT, nbTmin = bound_trucks(w, W)

    indxs = []
    for i in range(nbC):
        indxs = indxs + list(itertools.product([i], range(D[0][i][0]), range(nbT)))

    x = model.addVars(indxs, vtype=GRB.BINARY)
    y = model.addVars(range(nbT), vtype=GRB.BINARY)

    model.addConstrs(
        gp.quicksum(
            D[0][i][1] * x[i, j, k] for i in range(nbC) for j in range(D[0][i][0])
        )
        <= W * y[k]
        for k in range(nbT)
    )

    for i in range(nbC):
        for j in range(D[0][i][0]):
            model.addConstr(x.sum(i, j, "*") == 1)

    if symmetry_break:
        model.addConstrs(y[k] >= y[k + 1] for k in range(nbT - 1))

        for i in range(nbC):
            for j in range(D[0][i][0]):
                for k in range(nbT):
                    for jj in range(max(0, j - 1), j):
                        model.addConstr(
                            gp.quicksum(x[i, jj, kk] for kk in range(k + 1))
                            >= x[i, j, k]
                        )
                    for jj in range(j + 1, min(j + 2, D[0][i][0])):
                        model.addConstr(
                            gp.quicksum(x[i, jj, kk] for kk in range(k, nbT))
                            >= x[i, j, k]
                        )

    if knapsack:
        model.addConstr(gp.quicksum(W * y[i] for i in range(nbT)) >= sum(w))

    model.addConstr(gp.quicksum(y) >= nbTmin)

    obj = gp.quicksum(y)

    model.setObjective(obj, sense=GRB.MINIMIZE)

    model.optimize()

    P2T = [
        [
            D[0][i][1],
            [k for j in range(D[0][i][0]) for k in range(nbT) if x[i, j, k].X > 0],
        ]
        for i in range(nbC)
    ]
    T2P = [
        [
            k,
            [
                (i, j, D[0][i][1])
                for i in range(nbC)
                for j in range(D[0][i][0])
                if x[i, j, k].X > 0
            ],
        ]
        for k in range(nbT)
    ]
    return model.ObjVal, P2T, T2P


if __name__ == "__main__":
    objVal, P2T, T2P = solve_model(D)
