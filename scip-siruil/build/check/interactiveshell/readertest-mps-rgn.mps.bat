read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/rgn.mps"
write problem temp/rgn.mps.mps
presolve
write transproblem temp/rgn.mps_trans.mps
read temp/rgn.mps_trans.mps
optimize
read temp/rgn.mps.mps
optimize
validatesolve "82.1999974" "82.1999974"
quit
