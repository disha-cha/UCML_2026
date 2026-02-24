from pyscipopt import Model
from states import getState

INSTANCE = "/mnt/c/Users/disha/OneDrive/Documents/instances/case118_S5_T24_seed1.lp"

m = Model()
m.hideOutput(True)
m.readProblem(INSTANCE)

# tiny run, but ensure separation actually happens
m.setIntParam("separating/maxroundsroot", 2)
m.setIntParam("separating/maxrounds", 2)

# limits/nodes is Longint in your build
m.setLongintParam("limits/nodes", 1)

# optional safety
m.setRealParam("limits/time", 30.0)

m.optimize()

state = getState("learn1", m, round_num=0)

print("keys:", state.keys())
print("row_features:", len(state["row_features"]))
print("col_features:", len(state["col_features"]))
print("cut_features:", len(state["cut_features"]))
print("sepa_features:", len(state["sepa_features"]))
