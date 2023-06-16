import gurobipy as gp
from gurobipy import GRB

# =============================================================================
# This example is inspired from book : Practical Python AI projects, Serge Kruk
# https://github.com/sgkruk/Apress-AI/blob/master/diet_problem.py
# Below implementation is in Gurobi
# =============================================================================

def gen_diet_problem(nb_foods=5, nb_nutrients=4):
    from random import randint, uniform

    data = []
    ranges = [10 ** randint(2, 4) for i in range(nb_nutrients)]
    x = [randint(15, 25) for i in range(nb_foods)]  # this must be feasible
    MinNutrient = [0] * nb_nutrients
    MaxNutrient = [0] * nb_nutrients
    for food in range(nb_foods):
        nutrients = [randint(10, ranges[i]) for i in range(nb_nutrients)]
        minmax = [randint(0, x[food]), randint(x[food], 2 * x[food])]
        cost = round(100 * uniform(0, 10)) / 100
        v = nutrients + minmax + [cost]
        data.append(v)
    for j in range(nb_nutrients):
        b = sum([x[i] * data[i][j] for i in range(nb_foods)])
        MinNutrient[j] = randint(0, b)
        MaxNutrient[j] = randint(b, 2 * b)
    data.append(MinNutrient + ["", "", "", ""])
    data.append(MaxNutrient + ["", "", "", ""])
    return data


N = gen_diet_problem()

nbF, nbN = len(N) - 2, len(N[0]) - 3
FMin, FMax, FCost, NMin, NMax = nbN, nbN + 1, nbN + 2, nbF, nbF + 1

min_food = [N[i][FMin] for i in range(nbF)]
max_food = [N[i][FMax] for i in range(nbF)]

model = gp.Model("diet_problem")

# decision variables : number of servings of each food
food = model.addVars(range(nbF), lb=min_food, ub=max_food, vtype=GRB.CONTINUOUS)

# constraint : meet minimum and maximum nutritional requirements
for j in range(nbN):
    model.addConstr(gp.quicksum(food[i] * N[i][j] for i in range(nbF)) >= N[NMin][j])
    model.addConstr(gp.quicksum(food[i] * N[i][j] for i in range(nbF)) <= N[NMax][j])

cost = gp.quicksum(food[i] * N[i][FCost] for i in range(nbF))

model.setObjective(cost, sense=GRB.MINIMIZE)

model.optimize()
