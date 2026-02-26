read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/misc03.mps"
write problem temp/misc03.mps.pbm
presolve
write transproblem temp/misc03.mps_trans.pbm
read temp/misc03.mps_trans.pbm
optimize
read temp/misc03.mps.pbm
optimize
validatesolve "3360" "3360"
quit
