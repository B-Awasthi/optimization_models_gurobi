from random import randint, uniform
from math import sqrt
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB


def dist(p1, p2):
    return int(round(10 * sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)))


def gen_data(n):
    points = [(randint(1, 100), randint(1, 100)) for i in range(n)]
    R = [[None for i in range(n)] for j in range(n)]
    for i in range(n):
        for j in range(n):
            perturb = uniform(0.8, 1.2)
            if i != j and perturb > 0:
                R[i][j] = int(dist(points[i], points[j]) * perturb)
    return R


n = 15
D = gen_data(n)

cities = ["C_" + str(i) for i in range(1, n + 1)]
dist_cities = {}
for i in range(1, n + 1):
    for j in range(1, n + 1):
        if i != j and j > i:
            dist_cities[("C_" + str(i), "C_" + str(j))] = D[i - 1][j - 1]


model = gp.Model("TSP")

# Decision variables : is city 'i' adjacent to city 'j' on the tour?
dv = model.addVars(dist_cities.keys(), obj=dist_cities, vtype=GRB.BINARY, name="x")

# adding an edge in an opposite direction
for i, j in dv.keys():
    dv[j, i] = dv[i, j]

# Constraints: two edges incident to each city
cons = model.addConstrs(dv.sum(c, "*") == 2 for c in cities)


# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = gp.tuplelist(
            (i, j) for i, j in model._vars.keys() if vals[i, j] > 0.5
        )
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(cities):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(
                gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                <= len(tour) - 1
            )


# Given a tuplelist of edges, find the shortest subtour
def subtour(edges):
    unvisited = cities[:]
    cycle = cities[:]
    while unvisited:
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, "*") if j in unvisited]
        if len(thiscycle) <= len(cycle):
            cycle = thiscycle  # New shortest subtour
    return cycle


model._vars = dv
model.Params.lazyConstraints = 1
model.optimize(subtourelim)

# Retrieve solution

vals = model.getAttr("x", dv)
selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

tour = subtour(selected)
assert len(tour) == len(cities)
