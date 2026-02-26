read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/misc03.mps"
write problem temp/misc03.mps.cip
presolve
write transproblem temp/misc03.mps_trans.cip
read temp/misc03.mps_trans.cip
optimize
read temp/misc03.mps.cip
optimize
validatesolve "3360" "3360"
quit
