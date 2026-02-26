read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/blend2.mps"
write problem temp/blend2.mps.pip
presolve
write transproblem temp/blend2.mps_trans.pip
read temp/blend2.mps_trans.pip
optimize
read temp/blend2.mps.pip
optimize
validatesolve "7.598985" "7.598985"
quit
