read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/blend2.mps"
write problem temp/blend2.mps.pbm
presolve
write transproblem temp/blend2.mps_trans.pbm
read temp/blend2.mps_trans.pbm
optimize
read temp/blend2.mps.pbm
optimize
validatesolve "7.598985" "7.598985"
quit
