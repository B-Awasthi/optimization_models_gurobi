import itertools
import transship_dist
import gurobipy as gp
from gurobipy import GRB


# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/multi_commodity_flow.py
# Below implementation is in Gurobi
# =============================================================================


# function to generate data
def gen_data(n, K):
    C = [transship_dist.gen_data(n, False) for _ in range(K)]
    X = [[0 for _ in range(n)] for _ in range(n)]
    for k in range(K):
        status, Val, x = transship_dist.solve_model(C[k])
        if status == 2:  # optimal
            for i in range(n):
                for j in range(n):
                    try:
                        X[i][j] += x[i, j]
                    except KeyError:
                        X[i][j] += 0
    Cap = max([e for row in X for e in row])
    return C, Cap - 100


C, cap = gen_data(5, 3)

"""
gen_data(n, K)

n : number of supply and demand points (both same in number)
K : number of products

C : K lists of list
"""


def solve_model(C, D=None, Z=True):
    model = gp.Model("Multi-commodity mincost flow problem")

    K, n = (
        len(C),
        len(C[0]) - 1,
    )
    B = [sum(C[k][-1][j] for j in range(n)) for k in range(K)]

    indx = list(itertools.product(range(K), range(n), range(n)))
    upper_bound = [B[k] if C[k][i][j] else 0 for k, i, j in indx]

    x = model.addVars(indx, lb=0, ub=upper_bound, vtype=GRB.INTEGER)

    for k in range(K):
        for i in range(n):
            model.addConstr(
                C[k][i][-1] - C[k][-1][i] == x.sum(k, i, "*") - x.sum(k, "*", i)
            )

    if D:
        for i in range(n):
            for j in range(n):
                model.addConstr(
                    x.sum("*", i, j) <= D if type(D) in [int, float] else D[i][j]
                )
    Cost = gp.quicksum(
        C[k][i][j] * x[k, i, j] if C[k][i][j] else 0
        for i in range(n)
        for j in range(n)
        for k in range(K)
    )

    model.setObjective(Cost, sense=GRB.MINIMIZE)
    model.optimize()

    sol = {k: v for k, v in x.items() if v.X > 0}

    return model.status, model.ObjVal, sol


if __name__ == "__main__":
    optimality_status, objval, sol = solve_model(C)
