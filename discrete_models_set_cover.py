from random import randint, uniform
import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/set_cover.py
# Below implementation is in Gurobi
# =============================================================================


def gen_data(m, n):
    # m is number of subsets, n is the size of universe
    All = [0 for i in range(n)]
    while sum(All) < n:
        R = []
        All = [0 for i in range(n)]
        p = 0.8
        for i in range(m):
            RR = []
            for j in range(n):
                if uniform(0, 1) > p:
                    RR.append(j)
                    All[j] = 1
            R.append(RR)
    return R, [randint(1, 10) for i in range(m)]


D = gen_data(5, 10)

"""
D = gen_data(m, n)

m : number of suppliers
n : number of parts

D : D[0] represents which parts each supplier supplies
    D[1] is the cost for each supplier

"""


def solve_model(D):
    model = gp.Model("Set Cover")
    nbSup = len(D[0])
    parts = set([e for d in D[0] for e in d])

    supplier_part_dict = {}
    supplier_cost_dict = {}
    for ind, sup in enumerate(range(nbSup)):
        supplier_part_dict[sup] = D[0][ind]
        supplier_cost_dict[sup] = D[1][ind]

    supplier_cost_dict = gp.tupledict(supplier_cost_dict)

    part_supplier_dict = {}

    for prt in parts:
        part_supplier_dict[prt] = [k for k, v in supplier_part_dict.items() if prt in v]

    x = model.addVars(range(nbSup), vtype=GRB.BINARY)

    model.addConstrs(
        gp.quicksum(x[sup] for sup in part_supplier_dict[prt]) >= 1 for prt in parts
    )

    cost = supplier_cost_dict.prod(x)

    model.setObjective(cost, sense=GRB.MINIMIZE)
    model.optimize()

    Suppliers = [i for i in range(nbSup) if x[i].X > 0]
    Parts = {k: v for k, v in supplier_part_dict.items() if k in Suppliers}
    return model.ObjVal, Suppliers, Parts


if __name__ == "__main__":
    objVal, Suppliers, Parts = solve_model(D)
