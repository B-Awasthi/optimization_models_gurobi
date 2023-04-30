from random import randint
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/set_packing.py
# Below implementation is in Gurobi
# =============================================================================


def gen_data(m, n, k):
    # m is number of subsets, n is the size of universe, k is the size of each subset
    R = []
    for i in range(m):
        RR = []
        while len(RR) < k:
            p = randint(0, n)
            if p not in RR:
                RR.append(randint(0, n))
        RR.sort()
        R.append(RR)
    return R, [randint(1, 10) for i in range(m)]


D = gen_data(5, 15, 4)

"""
D = gen_data(m, n, k)

m : number of rosters
n : number of crews
k : length of the subset of crews in each roster

D : D[0] represents which crews belongs to each roster
    D[1] is the payoff for choosing each roster

"""


def solve_model(D, C=None):
    model = gp.Model("Set Packing")

    nbRosters = len(D[0])
    crews = set([e for d in D[0] for e in d])

    roster_crew_dict = {}
    roster_cost_dict = {}
    for ind, ros in enumerate(range(nbRosters)):
        roster_crew_dict[ros] = D[0][ind]
        roster_cost_dict[ros] = D[1][ind]

    roster_crew_num_dict = gp.tupledict(
        {k: len(set(v)) for k, v in roster_crew_dict.items()}
    )

    roster_cost_dict = gp.tupledict(roster_cost_dict)

    crew_roster_dict = {}

    for crw in crews:
        crew_roster_dict[crw] = [k for k, v in roster_crew_dict.items() if crw in v]

    x = model.addVars(range(nbRosters), vtype=GRB.BINARY)

    model.addConstrs(
        gp.quicksum(x[ros] for ros in crew_roster_dict[crw]) <= 1 for crw in crews
    )

    payoff = roster_crew_num_dict.prod(x)

    model.setObjective(payoff, sense=GRB.MAXIMIZE)

    model.optimize()

    Rosters = [i for i in range(nbRosters) if x[i].X > 0]
    return model.ObjVal, Rosters


if __name__ == "__main__":
    objVal, Rosters = solve_model(D)
