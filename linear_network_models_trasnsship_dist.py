from random import randint
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/transship_dist.py
# Below implementation is in Gurobi
# =============================================================================


# function to generate data
def gen_data(n, zap=True):
    R, Cap = [], []
    S, D = 0, 0
    for i in range(n):
        RR = []
        for j in range(n):
            if zap:
                yesno = randint(0, 1)
            else:
                yesno = 1
            if i != j and (i < j or randint(0, 1) * R[j][i] == 0):
                RR.append(yesno * randint(10, 30))
            else:
                RR.append(0)
        T = (0 if i == n - 1 else randint(0, 1) * randint(0, 1)) * randint(500, 700)
        RR.append(T)
        R.append(RR)
        S += T
    A = S / n
    RR = []
    for i in range(n - 1):
        if zap:
            yesno = 1 - (randint(0, 1) * randint(0, 1))
        else:
            yesno = 1
        T = (1 if R[i][-1] == 0 else 0) * yesno * randint(int(0.95 * A), int(1.9 * A))
        RR.append(T)
        D += T
    # Need to ensure balance
    T = S - D
    RR.append(T)
    D += T
    RR.append(0)
    R.append(RR)
    return R


D = gen_data(10)

"""
gen_data(n)

n : number of supply and demand points (both same in number)
D : is a 2 dimensional array indexed by n, n
D : last row of D represents the demand to be met for each demand points
D : last column represents the supply limit of each of the supply points
"""


def solve_model(D):
    model = gp.Model("Transshipment problem")
    n = len(D[0]) - 1
    B = sum([D[-1][j] for j in range(n)])

    nodes_list = [(i, j) for j in range(n) for i in range(n) if D[i][j] > 0]

    x = model.addVars(nodes_list, vtype=GRB.CONTINUOUS, lb=0, ub=B)

    model.addConstrs(
        D[i][-1] - D[-1][i] == x.sum(i, "*") - x.sum("*", i) for i in range(n)
    )

    cost = gp.quicksum(x[i, j] * D[i][j] for i, j in nodes_list)

    model.setObjective(cost, sense=GRB.MINIMIZE)
    model.optimize()

    solution = {i: x[i].X for i in x}

    return model.Status, model.ObjVal, solution


if __name__ == "__main__":
    optimality_status, objval, sol = solve_model(D)
