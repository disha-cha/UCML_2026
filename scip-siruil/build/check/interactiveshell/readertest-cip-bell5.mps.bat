read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/bell5.mps"
write problem temp/bell5.mps.cip
presolve
write transproblem temp/bell5.mps_trans.cip
read temp/bell5.mps_trans.cip
optimize
read temp/bell5.mps.cip
optimize
validatesolve "8966406.49" "8966406.49"
quit
