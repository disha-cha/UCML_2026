read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/bell5.mps"
write problem temp/bell5.mps.ppm
presolve
write transproblem temp/bell5.mps_trans.ppm
read temp/bell5.mps_trans.ppm
optimize
read temp/bell5.mps.ppm
optimize
validatesolve "8966406.49" "8966406.49"
quit
