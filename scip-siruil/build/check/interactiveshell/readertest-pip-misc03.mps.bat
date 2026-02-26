read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/misc03.mps"
write problem temp/misc03.mps.pip
presolve
write transproblem temp/misc03.mps_trans.pip
read temp/misc03.mps_trans.pip
optimize
read temp/misc03.mps.pip
optimize
validatesolve "3360" "3360"
quit
