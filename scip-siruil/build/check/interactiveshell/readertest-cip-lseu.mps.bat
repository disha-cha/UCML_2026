read "/home/disha/UCML_2026/scip-siruil"/check/"instances/MIP/lseu.mps"
write problem temp/lseu.mps.cip
presolve
write transproblem temp/lseu.mps_trans.cip
read temp/lseu.mps_trans.cip
optimize
read temp/lseu.mps.cip
optimize
validatesolve "1120" "1120"
quit
