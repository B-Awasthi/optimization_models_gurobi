from random import randint, sample
import collections
import itertools
import gurobipy as gp
from gurobipy import GRB


def gen_data(m, n):
    # m is number of jobs, n is the number of machines
    R = []
    for j in range(m):
        p = list(range(n))
        p = sample(p, len(p))
        RR = []
        for i in range(n):
            RR.append((p[i], randint(5, 10)))
        R.append(RR)
    return R


m = 3
n = 3
D = gen_data(m, n)

num_jobs = m
all_jobs = range(num_jobs)

num_machines = n
all_machines = range(num_machines)

durations = []
for i in all_jobs:
    tmp = []
    for j in all_machines:
        tmp.append(D[i][j][1])
    durations.append(tmp)

machines = []
for i in all_jobs:
    tmp = []
    for j in all_machines:
        tmp.append(D[i][j][0])
    machines.append(tmp)

model = gp.Model("jobshop_scheduling")

horizon = sum([D[i][k][1] for i in range(num_jobs) for k in range(num_machines)])

task_type = collections.namedtuple("task_type", "start end")

# Creates jobs.
all_tasks = {}
for i in all_jobs:
    for j in all_machines:
        start_var = model.addVar(0, horizon, name="start_" + str(i) + "_" + str(j))
        duration = durations[i][j]
        end_var = model.addVar(0, horizon, name="end_" + str(i) + "_" + str(j))
        model.addConstr(end_var - start_var == duration)
        all_tasks[(i, j)] = task_type(start=start_var, end=end_var)


# Create disjuctive constraints.
machine_to_jobs = {}
for i in all_machines:
    machines_jobs = []
    for j in all_jobs:
        for k in all_machines:
            if machines[j][k] == i:
                machines_jobs.append((all_tasks[(j, k)].start, all_tasks[(j, k)].end))
    machine_to_jobs[i] = machines_jobs
    # Add no-overlap constraint
    lst = list(itertools.combinations(range(len(machine_to_jobs[i])), 2))
    no_overlap_binary = model.addVars(len(lst), vtype="B")
    for m, n in enumerate(lst):
        one = machine_to_jobs[i][n[0]]
        two = machine_to_jobs[i][n[1]]
        model.addGenConstrIndicator(no_overlap_binary[m], 1, two[0] >= one[1])
        model.addGenConstrIndicator(no_overlap_binary[m], 0, two[1] <= one[0])

# Precedences inside a job.
for i in all_jobs:
    for j in range(0, num_machines - 1):
        model.addConstr(all_tasks[(i, j + 1)].start >= all_tasks[(i, j)].end)

# Makespan objective.
obj_var = model.addVar(0, horizon, name="makespan")
model.addGenConstrMax(obj_var, [all_tasks[(i, num_machines - 1)].end for i in all_jobs])

model.setObjective(obj_var, sense=GRB.MINIMIZE)

model.optimize()

# display solution
for i in all_jobs:
    for j in all_machines:
        print(
            "Job: "
            + str(i)
            + " "
            + "Machine: "
            + str(j)
            + " -> "
            + "START = "
            + str(all_tasks[(i, j)].start.X)
            + " and "
            + "END = "
            + str(all_tasks[(i, j)].end.X)
        )
print("\n")
print("Makespan = " + str(model.ObjVal))
