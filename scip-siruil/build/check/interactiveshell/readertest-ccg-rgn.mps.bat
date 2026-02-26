read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/rgn.mps"
write problem temp/rgn.mps.ccg
presolve
write transproblem temp/rgn.mps_trans.ccg
read temp/rgn.mps_trans.ccg
optimize
read temp/rgn.mps.ccg
optimize
validatesolve "82.1999974" "82.1999974"
quit
