read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/bell5.mps"
write problem temp/bell5.mps.gms
presolve
write transproblem temp/bell5.mps_trans.gms
read temp/bell5.mps_trans.gms
optimize
read temp/bell5.mps.gms
optimize
validatesolve "8966406.49" "8966406.49"
quit
