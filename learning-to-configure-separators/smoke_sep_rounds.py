import pyscipopt as pyopt
import numpy as np

INSTANCE = "/mnt/c/Users/disha/OneDrive/Documents/instances/case118_S5_T24_seed1.lp"

model = pyopt.Model()
model.hideOutput(False)
model.readProblem(INSTANCE)

model.setIntParam("separating/maxrounds", 5)
model.setIntParam("separating/maxroundsroot", 5)

model.optimize()

print("Solved.")
