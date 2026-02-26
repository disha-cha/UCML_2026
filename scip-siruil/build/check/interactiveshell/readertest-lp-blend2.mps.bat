read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/blend2.mps"
write problem temp/blend2.mps.lp
presolve
write transproblem temp/blend2.mps_trans.lp
read temp/blend2.mps_trans.lp
optimize
read temp/blend2.mps.lp
optimize
validatesolve "7.598985" "7.598985"
quit
