from random import randint
import gurobipy as gp
from gurobipy import GRB


# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/maxflow.py
# Below implementation is in Gurobi
# =============================================================================


# function to generate data
def gen_data(n):
    R, S, T = [], [], []
    for i in range(n):
        RR = []
        if i == 0:  # 0 is always a source
            S.append(i)
        elif i == n - 1:  # last is always a sink
            T.append(i)
        elif randint(0, 4) == 0:
            S.append(i)
        elif randint(0, 4) == 1:
            T.append(i)

        for j in range(n):
            yesno = randint(0, 1) * (i != j)
            RR.append(randint(10, 30) * yesno)
        R.append(RR)
    return R, S, T


C, S, T = gen_data(100)

"""
C : 2 dimensional array indexed by nodes, containing capacity of the arc between 2 nodes
S : source nodes
T : sink nodes
"""


def solve_model(C, S, T, unique=True):
    model = gp.Model("Maximum flow problem")
    n = len(C)
    nodes_list = [(i, j) for j in range(n) for i in range(n) if C[i][j] > 0]
    capacity = [C[i][j] for i, j in nodes_list]

    vertices = set([i[0] for i in nodes_list] + [i[1] for i in nodes_list])

    x = model.addVars(nodes_list, vtype=GRB.CONTINUOUS, lb=0, ub=capacity)

    B = sum(C[i][j] for i in range(n) for j in range(n))

    Flowout, Flowin = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=B), model.addVar(
        vtype=GRB.CONTINUOUS, lb=0, ub=B
    )

    # flow conservation
    model.addConstrs(
        (
            x.sum("*", j) - x.sum(j, "*") == 0
            for j in vertices
            if j not in S and j not in T
        ),
        "node",
    )

    model.addConstr(Flowout == gp.quicksum(x.sum(i, "*") for i in S))
    model.addConstr(Flowin == gp.quicksum(x.sum("*", i) for i in S))

    if not unique:
        model.setObjective(Flowout - Flowin, sense=GRB.MAXIMIZE)
    else:
        model.ModelSense = GRB.MAXIMIZE
        model.setObjectiveN(Flowout - Flowin, 0, 2, name="net_outflow")
        model.setObjectiveN(-Flowin, 1, 1, name="minus_inflow")

    model.optimize()
    solution = {i: x[i].X for i in x}

    return Flowout.X, Flowin.X, solution


if __name__ == "__main__":
    solve_model(C, S, T, unique=True)
