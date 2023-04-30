import gurobipy as gp
from gurobipy import GRB
import itertools

# =============================================================================
# Below is an implementation of an asignemnet problem formulated as a network
# flow problem
# data has been borrowed from :
# https://developers.google.com/optimization/assignment/assignment_example
# =============================================================================

num_workers = 5
num_tasks = 4


source = 0
workers = [1, 2, 3, 4, 5]
tasks = [6, 7, 8, 9]
sink = 10

# source to workers
nodes_source_workers = list(itertools.product([source], workers))
cost_source_workers = {i: 0 for i in nodes_source_workers}

# workers to tasks
nodes_workers_tasks = list(itertools.product(workers, tasks))
cost_workers_tasks = {
    i: j
    for i, j in zip(
        nodes_workers_tasks,
        [
            90,
            80,
            75,
            70,
            35,
            85,
            55,
            65,
            125,
            95,
            90,
            95,
            45,
            110,
            95,
            115,
            50,
            100,
            90,
            100,
        ],
    )
}

# tasks to sink
nodes_tasks_sink = list(itertools.product(tasks, [sink]))
cost_tasks_sink = {i: 0 for i in nodes_tasks_sink}

capacity_arc = 1

supplies = [num_tasks, 0, 0, 0, 0, 0, 0, 0, 0, 0, -num_tasks]

model = gp.Model("Assignment_network_flow")

nodes_list = nodes_source_workers + nodes_workers_tasks + nodes_tasks_sink

x = model.addVars(nodes_list, vtype=GRB.CONTINUOUS, lb=0, ub=capacity_arc)

model.addConstrs(
    supplies[ind] == x.sum(ind, "*") - x.sum("*", ind) for ind, i in enumerate(supplies)
)

all_costs = merge = {**cost_source_workers, **cost_workers_tasks, **cost_tasks_sink}

cost = x.prod(all_costs)

model.setObjective(cost, sense=GRB.MINIMIZE)
model.optimize()

solution = {i: x[i].X for i in x if x[i].X > 0}
