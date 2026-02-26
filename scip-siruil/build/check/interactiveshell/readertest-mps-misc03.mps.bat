read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/misc03.mps"
write problem temp/misc03.mps.mps
presolve
write transproblem temp/misc03.mps_trans.mps
read temp/misc03.mps_trans.mps
optimize
read temp/misc03.mps.mps
optimize
validatesolve "3360" "3360"
quit
