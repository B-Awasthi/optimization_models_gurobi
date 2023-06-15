import numpy as np
import gurobipy as gp
from gurobipy import GRB

# =========================== DATA ======================================
np.random.seed(1)
TOL = 1e-6
W_roll = 100  # roll width
I = list(range(5))  # item set
w = np.random.randint(1, 50, len(I)).tolist()  # width of each item
d = np.random.randint(1, 50, len(I)).tolist()  # demand of each item
patterns = np.diag([W_roll // w[i] for i in I]).tolist()  # initial patterns

# ========================= Master Problem ====================================
model = gp.Model("cutting_stock")
model.ModelSense = GRB.MINIMIZE
x = model.addVars(len(patterns), obj=1, vtype=GRB.CONTINUOUS, name="x")
c1 = model.addConstrs((patterns[i][i] * x[i] >= d[i] for i in I), name="c1")

# ======================= Subproblem and Iteration ============================
MAX_ITERATIONS = 100
it = 1

while it <= MAX_ITERATIONS:
    model.optimize()
    price = [c1[i].pi for i in I]

    sub_problem = gp.Model("sub_problem")
    sub_problem.ModelSense = GRB.MAXIMIZE
    use = sub_problem.addVars(I, obj=price, vtype=GRB.INTEGER, name="use")
    c2 = sub_problem.addConstr(gp.quicksum(w[i] * use[i] for i in I) <= W_roll)
    sub_problem.optimize()
    min_rc = 1 - sub_problem.objVal
    if min_rc < -TOL:
        patterns.append([int(use[i].x) for i in I])
        x[it + len(I)] = model.addVar(
            obj=1, vtype=GRB.CONTINUOUS, column=gp.Column(patterns[-1], c1.values())
        )

        # alternate but less efficient way of adding columns

        # del model
        # model = gp.Model('cutstock')
        # model.ModelSense = GRB.MINIMIZE
        # x = model.addVars(len(patterns), obj=1, vtype=GRB.CONTINUOUS, name='x')
        # c1 = model.addConstrs((gp.quicksum(patterns[j][i] * x[j] for j in range(len(x))) >= d[i] for i in I), name='c1')
        it += 1

    else:
        break

# ====================== Relaxed Model Result =================================
relaxed_result = [
    f"{v.x:.4f} * {patterns[p]}" for p, v in enumerate(model.getVars()) if v.x > TOL
]
relaxed_result.insert(0, f"Relaxed result = {model.objVal:.4f} rolls")

# ====================== Integer Model Result =================================
model.optimize()
integer_result = [
    f"{int(v.x)} * {patterns[p]}" for p, v in enumerate(model.getVars()) if v.x > TOL
]
integer_result.insert(0, f"Integer result = {int(model.objVal)} rolls")
