read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/rgn.mps"
write problem temp/rgn.mps.cip
presolve
write transproblem temp/rgn.mps_trans.cip
read temp/rgn.mps_trans.cip
optimize
read temp/rgn.mps.cip
optimize
validatesolve "82.1999974" "82.1999974"
quit
